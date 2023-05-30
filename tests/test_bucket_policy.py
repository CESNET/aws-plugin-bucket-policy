# -*- coding: utf-8 -*-

""" """

import pytest

from aws_plugin_bucket_policy.bp_classes import *

def test_public_bucket_ro(bp):
    bp.add_statements(
        BP_statement.public_bucket_ro('test_bucket'),
    )
    with open('public-bucket-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_rw_ro(bp):
    tenant = 'test_tenant1'
    bucket = 'test_bucket'
    bp.add_statements([
        BP_statement.share2users(
            [[tenant,'test_user0'], [tenant,'test_user1']], 'rw', bucket
        ),
        BP_statement.share2users(
            [[tenant,'test_user2']], 'ro', bucket
        ),
    ])
    with open('user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_alien_user_rw_ro(bp):
    bp.add_statements([
        BP_statement.share2users(
            [['test_tenant1','test_user0'], ['test_tenant2','test_user21']],
            'rw', 'test_bucket'
        ),
        BP_statement.share2users(
            [['test_tenant3','test_user31']], 'ro', 'test_bucket'
        ),
    ])
    with open('alien-user-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_tenant_rw_ro(bp):
    bp.add_statements([
        BP_statement.share2tenant('test_tenant1', 'rw', 'test_bucket'),
        BP_statement.share2tenant('test_tenant2', 'ro', 'test_bucket'),
    ])
    with open('tenant-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_prefix_rw_ro(bp):
    bp.add_statements([
        BP_statement.share2users(
            [['test_tenant1','test_user0']], 'rw', 'test_bucket'
        ),
        BP_statement.share_prefix2users(
            [['test_tenant1','test_user1']], 'rw', 'test_bucket', 'prefix1'
        ),
        BP_statement.share_prefix2users(
            [['test_tenant1','test_user2']], 'ro', 'test_bucket', 'prefix2'
        ),
    ])
    with open('user-prefix-rw-ro.json') as f:
        goldval = f.read()
        assert bp.save() == goldval

def test_user_prefix_rw_ro2(bp):
    bp.add_statements([
        BP_statement.share2users(
            [['test_tenant1','test_user0']], 'rw', 'test_bucket'
        ),
        BP_statement.share_prefix2users(
            [['test_tenant1','test_user1'],['test_tenant2','test_user21']], 'rw', 'test_bucket', 'prefix3'
        ),
        BP_statement.share_prefix2users(
            [['test_tenant1','test_user2'],['test_tenant2','test_user22']], 'ro', 'test_bucket', 'prefix4'
        ),
    ])
    with open('user-prefix-rw-ro2.json') as f:
        goldval = f.read()
        assert bp.save() == goldval
