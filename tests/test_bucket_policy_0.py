# -*- coding: utf-8 -*-

""" """

import pytest

from aws_plugin_bucket_policy.bucket_policy import *

def test_public_bucket_ro_0(bp):
    bp.add_statement(
        principal = BP_principal.public(),
        action = BP_action.ro(),
        resource = BP_resource.bucket('test_bucket')
    )
    with open('public-bucket-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_rw_ro_0(bp):
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.arn('test_tenant1','test_user0'),
            BP_principal.arn('test_tenant1','test_user1'),
        ]),
        action = BP_action.rw(),
        resource = BP_resource.bucket('test_bucket')
    )
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.arn('test_tenant1','test_user2'),
        ]),
        action = BP_action.ro(),
        resource = BP_resource.bucket('test_bucket')
    )
    with open('user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_rw_ro_1(bp):
    bp.add_statements([
        BP_statement.general(
            principal = BP_principal.users([
                BP_principal.arn('test_tenant1','test_user0'),
                BP_principal.arn('test_tenant1','test_user1'),
            ]),
            action = BP_action.rw(),
            resource = BP_resource.bucket('test_bucket')
        ),
        BP_statement.general(
            principal = BP_principal.users([
                BP_principal.arn('test_tenant1','test_user2'),
            ]),
            action = BP_action.ro(),
            resource = BP_resource.bucket('test_bucket')
        ),
    ])
    with open('user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_alien_user_rw_ro_0(bp):
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.arn('test_tenant1','test_user0'),
            BP_principal.arn('test_tenant2','test_user21'),
        ]),
        action = BP_action.rw(),
        resource = BP_resource.bucket('test_bucket')
    )
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.arn('test_tenant3','test_user31'),
        ]),
        action = BP_action.ro(),
        resource = BP_resource.bucket('test_bucket')
    )
    with open('alien-user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_alien_user_rw_ro_0(bp):
    bp.add_statements([
        BP_statement.general(
            principal = BP_principal.users([
                BP_principal.arn('test_tenant1','test_user0'),
                BP_principal.arn('test_tenant2','test_user21'),
            ]),
            action = BP_action.rw(),
            resource = BP_resource.bucket('test_bucket')
        ),
        BP_statement.general(
            principal = BP_principal.users([
                BP_principal.arn('test_tenant3','test_user31'),
            ]),
            action = BP_action.ro(),
            resource = BP_resource.bucket('test_bucket')
        ),
    ])
    with open('alien-user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def tenant_rw_ro_0(bp):
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.tenant('test_tenant1'),
        ]),
        action = BP_action.rw(),
        resource = BP_resource.bucket('test_bucket')
    )
    bp.add_statement(
        principal = BP_principal.users([
            BP_principal.tenant('test_tenant2'),
        ]),
        action = BP_action.ro(),
        resource = BP_resource.bucket('test_bucket')
    )
    with open('tenant-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_tenant_rw_ro_1(bp):
    bp.add_statements([
        BP_statement.general(
            principal = BP_principal.tenant('test_tenant1'),
            action = BP_action.rw(),
            resource = BP_resource.bucket('test_bucket')
        ),
        BP_statement.general(
            principal = BP_principal.tenant('test_tenant2'),
            action = BP_action.ro(),
            resource = BP_resource.bucket('test_bucket')
        ),
    ])
    with open('tenant-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_prefix_rw_ro_0(bp):
    bp.add_statements([
        BP_statement.general(
            principal = BP_principal.users([
                BP_principal.arn('test_tenant1','test_user0'),
            ]),
            action = BP_action.rw(),
            resource = BP_resource.bucket('test_bucket')
        ),
        BP_statement.prefix(
            users = [ BP_principal.arn('test_tenant1', 'test_user1'), ],
            action = BP_action.rw(),
            bucket_name = 'test_bucket',
            prefix_name = 'prefix1'
        ),
        BP_statement.prefix(
            users = [ BP_principal.arn('test_tenant1', 'test_user2'), ],
            action = BP_action.ro(),
            bucket_name = 'test_bucket',
            prefix_name = 'prefix2'
        ),
    ])
    with open('user-prefix-rw-ro.json') as f:
        goldval = f.read()
#        print(bp.save())
#        with open('./user-folder-rw-ro_GENER.json', 'w') as f1:
#            f1.write(bp.save())
#        print(bp.get_json())
        assert bp.save() == goldval
