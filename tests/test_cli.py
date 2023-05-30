# -*- coding: utf-8 -*-

""" """

import pytest, re
from awscli.testutils import mock, unittest, BaseAWSCommandParamsTest

from aws_plugin_bucket_policy.bucket_policy import *
from aws_plugin_bucket_policy.constants import *
from aws_plugin_bucket_policy import *

class CLITest(unittest.TestCase):
    def setUp(self):
        self.cli = mock.Mock()

    def test_initialize(self):
        awscli_initialize(self.cli)
        ref = []
        ref.append("building-command-table.main")
        ref.append("building-command-table.sync")
        for arg in self.cli.register.call_args_list:
            self.assertIn(arg[0][0], ref)

    def test_service(self):
        self.cli.name = 's3bucket-policy'
        self.services = {'s3bucket-policy': self.cli}
        Bucket_policy_command.add_command(self.services, True)
        for service in self.services.keys():
            self.assertIn(service, ['s3bucket-policy'])

class TestS3_1(BaseAWSCommandParamsTest):
    def setUp(self):
        super(TestS3_1, self).setUp()
        awscli_initialize(self.driver.session.get_component('event_emitter'))

    def test_no_subcomm(self):
        stdout, stderr, _ = self.run_cmd('s3bucket-policy', expected_rc=255)
        self.assertIn('no subcommand specified', stdout)

    def test_get_policy_wo_bucket(self):
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Buckets': [ {'Name':'b1'}, {'Name':'b2'}, {'Name':'b3'}, ]
        }
        stdout, stderr, _ = self.run_cmd('s3bucket-policy get-policy --nonint', expected_rc=100)
        assert stdout == "['b1', 'b2', 'b3']\n"
        assert stderr == ''

    def test_get_policy(self):
        bucket_name = 'test-bucket1'
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Policy': '{"Statement":[{"Effect":"Allow"}]}',
        }
        stdout, stderr, _ = self.run_cmd(f's3bucket-policy get-policy --nonint --bucket {bucket_name}', expected_rc=0)
        self.assertIn(f'Bucket "{bucket_name}"', stdout)
        self.assertIn(f'"Statement":', stdout)
        rer = re.match(r'^Bucket "[-a-zA-Z0-9]+" policy:\s*({[\sa-zA-Z0-9":\[\]{}]*})$', stdout)
        assert rer
        policy = json.loads(rer[1])
        assert len(policy['Statement']) == 1
        assert policy['Statement'][0]['Effect'] == 'Allow'
        assert stderr == ''

    def test_new_policy_ro_public(self):
        bucket_name = 'test-bucket1'
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Policy': '{"Statement":[{"Effect":"Allow"}]}',
            'Owner': {'ID':'tenant1$user1'}
        }
        stdout, stderr, _ = self.run_cmd(f's3bucket-policy new-policy --nonint --bucket {bucket_name} --quiet --newpol-type ro-public', expected_rc=0)
        self.assertIn(f'"Statement":', stdout)
        rx =r'^\s*{[^{}]+{[^{}]+}[^{}]+}\s*---\s*({[-a-zA-Z0-9:"\[\]{}\s/*,]+})\s*{.+}$'
        self.assertRegex(stdout, rx)
        rer = re.match(rx, stdout)
        assert rer
        policy = json.loads(rer[1])
        assert len(policy['Statement']) == 1
        assert policy['Statement'][0]['Effect'] == 'Allow'
        assert policy['Statement'][0]['Principal'] == "*"
        assert len(policy['Statement'][0]['Action']) == 2
        assert len(policy['Statement'][0]['Resource']) == 2
        self.assertRegex(policy['Statement'][0]['Resource'][0], f'^arn:aws:s3:::{bucket_name}$')
        assert stderr == ''

    def test_new_policy_share_w_user(self):
        bucket_name = 'test-bucket1'
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Policy': '{"Statement":[{"Effect":"Allow"}]}',
            'Owner': {'ID':'tenant1$user1'}
        }
        stdout, stderr, _ = self.run_cmd(
            f's3bucket-policy new-policy --nonint --bucket {bucket_name} --quiet'
            ' --newpol-type share-w-user --newpol-spec tenant=ten1,user=u1,action=rw tenant=ten2,user=u2,action=ro',
            expected_rc=0
        )
        self.assertIn(f'"Statement":', stdout)
        rx =r'^\s*{[^{}]+{[^{}]+}[^{}]+}\s*---\s*({[-a-zA-Z0-9:"\[\]{}\s/*,]+})\s*{.+}$'
        self.assertRegex(stdout, rx)
        rer = re.match(rx, stdout)
        assert rer
        policy = json.loads(rer[1])
        assert len(policy['Statement']) == 2
        assert policy['Statement'][0]['Effect'] == 'Allow'
        assert len(policy['Statement'][0]['Principal']['AWS']) == 2
        assert len(policy['Statement'][0]['Action']) == 4
        assert len(policy['Statement'][0]['Resource']) == 2
        self.assertRegex(policy['Statement'][0]['Resource'][0], f'^arn:aws:s3:::{bucket_name}$')
        assert policy['Statement'][1]['Effect'] == 'Allow'
        assert len(policy['Statement'][1]['Principal']['AWS']) == 1
        assert len(policy['Statement'][1]['Action']) == 2
        assert len(policy['Statement'][1]['Resource']) == 2
        self.assertRegex(policy['Statement'][1]['Resource'][1], f'^arn:aws:s3:::{bucket_name}/\\*$')
        assert stderr == ''

    def test_new_policy_share_w_tenant(self):
        bucket_name = 'test-bucket1'
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Policy': '{"Statement":[{"Effect":"Allow"}]}',
            'Owner': {'ID':'tenant1$user1'}
        }
        stdout, stderr, _ = self.run_cmd(
            f's3bucket-policy new-policy --nonint --bucket {bucket_name} --quiet'
            ' --newpol-type share-w-tenant --newpol-spec tenant=tenant1,action=rw tenant=tenant2,action=ro',
            expected_rc=0
        )
        self.assertIn(f'"Statement":', stdout)
        rx =r'^\s*{[^{}]+{[^{}]+}[^{}]+}\s*---\s*({[-a-zA-Z0-9:"\[\]{}\s/*,]+})\s*{.+}$'
        self.assertRegex(stdout, rx)
        rer = re.match(rx, stdout)
        assert rer
        policy = json.loads(rer[1])
        assert len(policy['Statement']) == 2
        assert policy['Statement'][0]['Effect'] == 'Allow'
        assert policy['Statement'][0]['Principal']['AWS'][0] == 'tenant1'
        assert len(policy['Statement'][0]['Action']) == 4
        assert len(policy['Statement'][0]['Resource']) == 2
        self.assertRegex(policy['Statement'][0]['Resource'][0], f'^arn:aws:s3:::{bucket_name}$')
        assert policy['Statement'][1]['Effect'] == 'Allow'
        assert policy['Statement'][1]['Principal']['AWS'][0] == 'tenant2'
        assert len(policy['Statement'][1]['Action']) == 2
        assert len(policy['Statement'][1]['Resource']) == 2
        self.assertRegex(policy['Statement'][1]['Resource'][1], f'^arn:aws:s3:::{bucket_name}/\\*$')
        assert stderr == ''

    def test_new_policy_share_prefix_w_user(self):
        bucket_name = 'test-bucket1'
        prefix1 = 'pref1'
        prefix2_hex = 'pref2%20a%3db%%c'
        prefix2 = 'pref2 a=b%c'
        self.parsed_response = {
            'ResponseMetadata': { 'HTTPStatusCode': 200, },
            'Policy': '{"Statement":[{"Effect":"Allow"}]}',
            'Owner': {'ID':'tenant1$user1'}
        }
        stdout, stderr, _ = self.run_cmd(
            f's3bucket-policy new-policy --nonint --bucket {bucket_name} --quiet'
            f' --newpol-type share-prefix-w-user --newpol-spec tenant=ten1,user=u1,action=rw,prefix={prefix1} tenant=ten2,user=u2,action=ro,prefix={prefix2_hex}',
            expected_rc=0
        )
        self.assertIn(f'"Statement":', stdout)
        rx =r'^\s*{[^{}]+{[^{}]+}[^{}]+}\s*---\s*({[-a-zA-Z0-9:"\[\]{}\s/*, =%]+})\s*{.+}$'
        self.assertRegex(stdout, rx)
        rer = re.match(rx, stdout)
        assert rer
        policy = json.loads(rer[1])
#        assert policy == []
        assert len(policy['Statement']) == 5
        assert policy['Statement'][0]['Effect'] == 'Allow'
        assert len(policy['Statement'][0]['Principal']['AWS']) == 1
        assert len(policy['Statement'][0]['Action']) == 4
        assert len(policy['Statement'][0]['Resource']) == 2
        self.assertRegex(policy['Statement'][0]['Resource'][0], f'^arn:aws:s3:::{bucket_name}$')
        assert policy['Statement'][0] == {
            'Action': ['s3:ListBucket','s3:GetObject','s3:PutObject','s3:DeleteObject'],
            'Effect': 'Allow',
            'Principal': {'AWS': ['arn:aws:iam::tenant1:user/user1']},
            'Resource': [f'arn:aws:s3:::{bucket_name}',f'arn:aws:s3:::{bucket_name}/*'],
            'Sid': policy['Statement'][0]['Sid']
        }
        assert policy['Statement'][1]['Effect'] == 'Allow'
        assert len(policy['Statement'][1]['Principal']['AWS']) == 1
        assert len(policy['Statement'][1]['Action']) == 4
        assert len(policy['Statement'][1]['Resource']) == 2
        self.assertRegex(policy['Statement'][1]['Resource'][1], f'^arn:aws:s3:::{bucket_name}/{prefix1}/\\*$')
        assert policy['Statement'][1]['Effect'] == 'Allow'
        assert len(policy['Statement'][2]['Principal']['AWS']) == 1
        assert len(policy['Statement'][2]['Action']) == 1
        assert len(policy['Statement'][2]['Resource']) == 1
        assert policy['Statement'][2]['Resource'][0] == f'arn:aws:s3:::{bucket_name}'
        assert policy['Statement'][2]['Condition']['StringEquals']['s3:delimiter'] == ['/']
        assert policy['Statement'][2]['Condition']['StringLike']['s3:prefix'] == [f'{prefix1}/*']
        assert policy['Statement'][3] == {
            'Action': ['s3:ListBucket','s3:GetObject'],
            'Effect': 'Allow',
            'Principal': {'AWS': ['arn:aws:iam::ten2:user/u2']},
            'Resource': [f'arn:aws:s3:::{bucket_name}/{prefix2}',f'arn:aws:s3:::{bucket_name}/{prefix2}/*'],
            'Sid': policy['Statement'][3]['Sid']
        }
        assert policy['Statement'][4] == {
            'Action': ['s3:ListBucket'],
            'Condition': {
                'StringEquals': {'s3:delimiter': ['/']},
                'StringLike': {'s3:prefix': [f'{prefix2}/*']}
            },
            'Effect': 'Allow',
            'Principal': {'AWS': ['arn:aws:iam::ten2:user/u2']},
            'Resource': [f'arn:aws:s3:::{bucket_name}'],
            'Sid': policy['Statement'][4]['Sid']
        }
        assert stderr == ''
