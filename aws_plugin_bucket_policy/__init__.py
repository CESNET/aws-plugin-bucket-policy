# -*- coding: utf-8 -*-
#
"""
  AWScli bucket-policy manipulation plugin
  Copyright (C) 2023 CESNET
  hlava@cesnet.cz

  get-policy
  new-policy
  delete-policy
  put-policy
  statement
      list
      delete

"""

import sys, json
from awscli.customizations.commands import BasicCommand
from botocore.config import Config
from botocore.exceptions import ClientError
from .bucket_policy import *
from .utils import *
from .constants import *

NONINT_ARG = {'name':'nonint', 'help_text':'Disable interactive UI', 'action':'store_true'}
NO_FZF_ARG = {'name':'nofzf', 'help_text':'Disable fzf support', 'action':'store_true'}
QUIET_ARG = {'name':'quiet', 'help_text':'Low verbosity output', 'action':'store_true'}
DRYRUN_ARG = {'name':'dryrun', 'help_text':'Dry run with all write ops disabled', 'action':'store_true'}
BUCKET_ARG = {'name':'bucket', 'help_text':'Bucket name'}
BUCKET_REQ_ARG = {'name':'bucket', 'help_text':'Bucket name', 'required':True}
BASIC_ARGS = [ BUCKET_ARG, NO_FZF_ARG, NONINT_ARG, QUIET_ARG, DRYRUN_ARG ]

POLICY_ARG = {'name':'policy', 'help_text':'Policy file name'}
NEWPOL_CHOICES = ['ro-public', 'share-w-user', 'share-w-tenant', 'share-prefix-w-user']
NEWPOL_type = {'name':'newpol-type', 'choices': NEWPOL_CHOICES,
        'help_text': (
            'New bucket policy use-case.'
            ' "ro-public": public read-only bucket;'
            ' "share-w-user": bucket shared with specified users;'
            ' "share-w-tenant": bucket shared with all users from specified tenants.'
            ' "share-prefix-w-user": prefix in bucket shared with specified users;'
        )
    }
NEWPOL_SPEC = {'name':'newpol-spec', 'nargs':'+',
        'help_text': (
            'New bucket policy use-case specification.'
            ' newpol-type "ro-public": not applicable;'
            ' newpol-type "share-w-user": "tenant=TENANT_NAME,user=USER_NAME,action=[rw|ro]" can be repeated;'
            ' newpol-type "share-w-tenant": "tenant=TENANT_NAME,action=[rw|ro]" can be repeated.'
            ' newpol-type "share-prefix-w-user": "tenant=TENANT_NAME,user=USER_NAME,action=[rw|ro],prefix=PREFIX" can be repeated,'
            ' prefix could contain url-like "%hex" characters (e.g. "=" as "%3d" and "%" as "%%");'
        )
    }
NEWPOL_ARGS = [ NEWPOL_type, NEWPOL_SPEC ]

class S3Command(BasicCommand):
    def _run_main(self, parsed_args, parsed_globals):
        client_config = Config(signature_version='s3v4')
        self.client = self._session.create_client('s3',
          region_name=parsed_globals.region,
          endpoint_url=parsed_globals.endpoint_url,
          verify=parsed_globals.verify_ssl,
          config=client_config
        )
        self._debug = parsed_globals.debug
        self._nofzf = parsed_args.nofzf
        self._nonint = parsed_args.nonint
        self._quiet = parsed_args.quiet
        self._dryrun = parsed_args.dryrun

    def select_bucket(self):
        apiresp = self.client.list_buckets()
        buckets = [b['Name'] for b in apiresp['Buckets']]
        if self._nonint: return buckets
        bn = sel(buckets, self._nofzf)
        return bn

    def get_bucket_owner(self, bn):
        apiresp = self.client.get_bucket_acl(Bucket=bn)
        if 'Owner' in apiresp and 'ID' in apiresp['Owner']:
            rer = re.match(r'^((.+)\$)?(.+)$', apiresp['Owner']['ID'])
            if rer:
                return { 'tenant': rer[2], 'user': rer[3] }
        raise Exception(f'Unknown or invalid bucket owner (bucket: {bn}, owner from API: "{apiresp["Owner"]["ID"]}")')

    def _cb_bucketSet(self, buckets):
        print(buckets)
        return E_BUCKETSET
    def _cb_noBucketPolicy(self, bn):
        self.bp = BucketPolicy("", quiet=self._quiet)
        self.bp.print(f"Bucket \"{bn}\" ")
        return W_NOBUCKETPOLICY
    def run_on_bucket(self, bn, cb_bucketSet, cb_bucket, cb_noBucketPolicy):
        if bn is None:
            bn = self.select_bucket()
            if self._nonint: return cb_bucketSet(bn)
        if bn is not None:
            self.bn = bn
            try:
                apiresp = self.client.get_bucket_policy(Bucket=bn)
                return cb_bucket(apiresp)
            except ClientError as e:
                if hasattr(e, 'response') and e.response.get('Error',{}).get('Code','Unknown') == "NoSuchBucketPolicy":
                    return cb_noBucketPolicy(bn)
                else: raise Exception("Boto3 client error: " + e.__str__())
            except Exception as e:
                raise Exception("Unknown exception: " + e.__str__())

class Subcommand_get_policy(S3Command):
    NAME = 'get-policy'
    DESCRIPTION = "Get bucket policy"
    USAGE = ""
    ARG_TABLE = BASIC_ARGS
    def _cb_bucket(self, apiresp):
        BucketPolicy(apiresp['Policy'], quiet=self._quiet).print(f"Bucket \"{self.bn}\"")
        return 0
    def _run_main(self, parsed_args, parsed_globals):
        super(Subcommand_get_policy, self)._run_main(parsed_args, parsed_globals)
        self.bn = parsed_args.bucket
        r = self.run_on_bucket(self.bn, self._cb_bucketSet, self._cb_bucket, self._cb_noBucketPolicy)
        if r >= MINERRID: sys.exit(r)
        return r

class Subcommand_delete_policy(Subcommand_get_policy):
    NAME = 'delete-policy'
    DESCRIPTION = "Delete bucket policy"
    USAGE = ""
    ARG_TABLE = BASIC_ARGS
    def _run_main(self, parsed_args, parsed_globals):
        r = super(Subcommand_delete_policy, self)._run_main(parsed_args, parsed_globals)
        if not self._dryrun:
            apiresp = self.client.delete_bucket_policy(Bucket=self.bn)
            print(apiresp)
        return r

class Subcommand_new_policy(Subcommand_get_policy):
    NAME = 'new-policy'
    DESCRIPTION = "Define and upload new bucket policy"
    USAGE = ""
    ARG_TABLE = BASIC_ARGS + NEWPOL_ARGS
    def _cb_bucket(self, apiresp):
        type = self._parsed_args.newpol_type
        spec = self._parsed_args.newpol_spec
        owner = self.get_bucket_owner(self.bn)
        self.bp = BucketPolicy(apiresp['Policy'], quiet=self._quiet)
        self.bp.print(f"Bucket \"{self.bn}\" old")
        if type in NEWPOL_CHOICES:
            r = self.bp.new_policy(self.bn, type, spec, owner)
        return 0
    def _cb_noBucketPolicy(self, bn):
        return self._cb_bucket({'Policy':""})
    def _run_main(self, parsed_args, parsed_globals):
        self._parsed_args = parsed_args
        r = super(Subcommand_new_policy, self)._run_main(parsed_args, parsed_globals)
        print("---")
        self.bp.print(f"Bucket \"{self.bn}\" new")
        policy_str = self.bp.save(indent=0)
        if not self._dryrun:
            apiresp = self.client.put_bucket_policy(Bucket=self.bn, Policy=policy_str)
            print(apiresp)
        return r

class Subcommand_put_policy(Subcommand_get_policy):
    NAME = 'put-policy'
    DESCRIPTION = "Put bucket policy"
    USAGE = "<sc_arg1>"
    ARG_TABLE = BASIC_ARGS+[POLICY_ARG]
    def _run_main(self, parsed_args, parsed_globals):
        r = super(Subcommand_put_policy, self)._run_main(parsed_args, parsed_globals)
        input = parsed_args.policy
        with open(input, 'r') as f:
            policy_str = f.read()
            json_obj = json.loads(policy_str)
            if not self._dryrun:
                apiresp = self.client.put_bucket_policy(Bucket=self.bn, Policy=policy_str)
                print(apiresp)
                if apiresp['ResponseMetadata']['HTTPStatusCode'] != 204:
                    raise Exception(f'Wrong API response status code ({apiresp}).')
        return r

class Subcommand_statement_list(Subcommand_get_policy):
    NAME = 'list'
    DESCRIPTION = "Get bucket policy statements"
    USAGE = ""
    ARG_TABLE = BASIC_ARGS
    def _cb_bucket(self, apiresp):
        BucketPolicy(apiresp['Policy'], quiet=self._quiet).print_statement_list()
        return 0

class Subcommand_statement_delete(S3Command):
    NAME = 'delete'
    DESCRIPTION = ""
    USAGE = ""
    ARG_TABLE = BASIC_ARGS
    def _run_main(self, parsed_args, parsed_globals):
        super(Subcommand_statement_delete, self)._run_main(parsed_args, parsed_globals)
        print('statement_delete NOT impl.', self._nofzf, self._nonint)

class Subcommand_statement(S3Command):
    NAME = 'statement'
    DESCRIPTION = ""
    USAGE = ""
    SUBCOMMANDS = [
        {'name':'list', 'command_class': Subcommand_statement_list},
        {'name':'delete', 'command_class': Subcommand_statement_delete},
    ]
#    ARG_TABLE = BASIC_ARGS
    def _run_main(self, parsed_args, parsed_globals):
        super(Subcommand_statement, self)._run_main(parsed_args, parsed_globals)
        print('Subcommand_statement: no 3rd level subcommand specified.')
        if self._debug: print(parsed_globals)

class Bucket_policy_command(S3Command):
    NAME = 's3bucket-policy'
    DESCRIPTION = "S3 Bucket policy manipulation awscli plugin"
    SYNOPSIS = "aws s3bucket-policy <Command> [<Arg> ...]"
    SUBCOMMANDS = [
        {'name':'get-policy', 'command_class': Subcommand_get_policy},
        {'name':'delete-policy', 'command_class': Subcommand_delete_policy},
        {'name':'new-policy', 'command_class': Subcommand_new_policy},
        {'name':'put-policy', 'command_class': Subcommand_put_policy},
#        {'name':'statement', 'command_class': Subcommand_statement},
    ]
#    ARG_TABLE = [ NO_FZF_ARG, NONINT_ARG ]
#    ARG_TABLE = [ NO_FZF_ARG, ]
    def _run_main(self, parsed_args, parsed_globals):
        self._debug = parsed_globals.debug
#        self._nofzf = parsed_args.nofzf
#        self._nonint = parsed_args.nonint
        print('Bucket_policy_command: no subcommand specified.')
        if self._debug: print(parsed_globals)
        if parsed_args.subcommand is None:
            raise ValueError("")

def awscli_initialize(cli):
    cli.register('building-command-table.main', Bucket_policy_command.add_command)

