# -*- coding: utf-8 -*-
#
"""
"""

import json, re
from copy import deepcopy

from .constants import *

class BP_principal():
    def __init__(self, tpl):
        self.principal = deepcopy(tpl)

    def get(self):
        return self.principal

    @classmethod
    def public(cls):
        return cls(PRINCIPAL_PUBLIC)

    @classmethod
    def tenant(cls, tenant_name):
        obj = cls(PRINCIPAL_AWS)
        obj.principal['AWS'].append(PRINCIPAL_TENANT.format(TENANT_NAME=tenant_name))
        return obj

    @classmethod
    def arn(cls, tenant_name, user_name):
        return PRINCIPAL_USER.format(TENANT_NAME=tenant_name, USER_NAME=user_name)

    @classmethod
    def u2arn(cls, tenant, u):
        if isinstance(u, list): return cls.arn(u[0], u[1])
        if isinstance(u, str): return cls.arn(tenant, u)
        else: raise Exception(f"Unsupported type in user array ({type(u)})")

    @classmethod
    def users(cls, user_arns=[]):
        obj = cls(PRINCIPAL_AWS)
        for u in user_arns: obj.principal['AWS'].append(u)
        return obj

    @classmethod
    def map(cls, pr):
        if pr == "*": return "public"
        elif 'AWS' in pr:
            rer = re.match(r'^arn:aws:iam::([-a-zA-Z0-9_]+):user/([-a-zA-Z0-9_]+)$', pr['AWS'][0])
            if rer: return f"User \"{rer[1]}${rer[2]}\""
            else:
                rer_tenant = re.match(r'^([a-zA-Z0-9_]+)$', pr['AWS'][0])
                if rer_tenant: return f"All users in tenant \"{rer_tenant[1]}\""
                else: return pr
        else: return pr

# --------------------------------------------------------------
class BP_action():
    def __init__(self, tpl):
        self.action = deepcopy(tpl)

    def get(self):
        return self.action

    @classmethod
    def rw(cls):
        return cls(ACTION_RW)

    @classmethod
    def ro(cls):
        return cls(ACTION_RO)

    @classmethod
    def list(cls):
        return cls(ACTION_LI)

    @classmethod
    def all(cls):
        return cls(ACTION_ALL)

    @classmethod
    def map(cls, action):
        ac_map = {
            json.dumps(ACTION_RW): "RW", json.dumps(ACTION_RO): "RO",
            json.dumps(ACTION_LI): "List", json.dumps(ACTION_ALL): "All perms",
        }
        ac_json = json.dumps(action)
        ac_str = ac_map[ac_json] if ac_json in ac_map else action
        return ac_str

    @classmethod
    def rmap(cls, ac):
        ac_rmap = {
            "RW": cls.rw(), "RO": cls.ro(), "LI": cls.list(), "ALL": cls.all(),
        }
        acu = ac.upper()
        action = ac_rmap[acu] if acu in ac_rmap else ac
        return action

# --------------------------------------------------------------
class BP_resource():
    def __init__(self, tpl):
        self.resource = deepcopy(tpl)

    def get(self):
        return self.resource

    @classmethod
    def bucket(cls, bucket_name):
        obj = cls(RESOURCE_BUCKET)
        rsc = obj.resource
        for i in range(len(rsc)): rsc[i] = rsc[i].format(BUCKET_NAME=bucket_name)
        return obj

    @classmethod
    def prefix(cls, bucket_name, prefix_name):
        obj = cls(RESOURCE_PREFIX)
        rsc = obj.resource
        for i in range(len(rsc)): rsc[i] = rsc[i].format(BUCKET_NAME=bucket_name, PREFIX_NAME=prefix_name)
        return obj

    @classmethod
    def list_condition(cls, bucket_name):
        obj = cls(RESOURCE_LIST_COND)
        rsc = obj.resource
        for i in range(len(rsc)): rsc[i] = rsc[i].format(BUCKET_NAME=bucket_name)
        return obj

    @classmethod
    def map(cls, rscs):
        r = []
        for rsc in rscs:
            rer = re.match(r'^arn:aws:s3:::([-a-zA-Z0-9]+)(/([^/]+)(/(\*))?)?$', rsc)
            if rer: r.append(f"{rer[1]}{'/'+rer[3] if rer[3] is not None else ''}{'/'+rer[5] if rer[5] is not None else ''}")
            else: r.append('Unsupp.resource type')
        return ', '.join(r)

# --------------------------------------------------------------
class BP_condition():
    def __init__(self, tpl):
        self.condition = deepcopy(tpl)

    def get(self):
        return self.condition

    @classmethod
    def prefix(cls, prefix_name):
        obj = cls(CONDITION_LIST)
        cond = obj.condition
        cond['StringLike']['s3:prefix'][0] = cond['StringLike']['s3:prefix'][0].format(PREFIX_NAME=prefix_name)
        return obj

# --------------------------------------------------------------
class BP_statement():
    def __init__(self, tpl, id=None, principal={}, action=ACTION_RO, resource=[], condition=None):
        self.statement = deepcopy(tpl)
        if id != None: self.set_id(id)
        self.statement['Principal'] = principal.get()
        self.statement['Action'] = action.get()
        self.statement['Resource'] = resource.get()
        if condition != None: self.statement['Condition'] = condition.get()

    def set_id(self, id=''):
        self.statement['Sid'] = self.statement['Sid'].format(STATEMENT_ID=id)

    def get(self):
        return self.statement

    @classmethod
    def statement(cls, tpl, id='', principal={}, action=ACTION_RO, resource=[]):
        return cls(tpl, id, principal, action, resource).statement

    @classmethod
    def general(cls, principal={}, action=ACTION_RO, resource=[], condition=None):
        return cls(STATEMENT_TPL,
            principal = principal, action = action, resource = resource, condition=condition
        )

    @classmethod
    def public_bucket_ro(cls, bucket_name):
        return cls(STATEMENT_TPL,
            principal = BP_principal.public(),
            action = BP_action.ro(),
            resource = BP_resource.bucket(bucket_name)
        )

    @classmethod
    def share2users(cls, users, ac='ro', bucket_name=None):
        return cls(STATEMENT_TPL,
            principal = BP_principal.users([BP_principal.u2arn(t, u) for (t,u) in users]),
            action = BP_action.rmap(ac),
            resource = BP_resource.bucket(bucket_name)
        )

    @classmethod
    def share2tenant(cls, tenant, ac='ro', bucket_name=None):
        return cls(STATEMENT_TPL,
            principal = BP_principal.tenant(tenant),
            action = BP_action.rmap(ac),
            resource = BP_resource.bucket(bucket_name)
        )

    @classmethod
    def share_prefix2users(cls, users, ac='ro', bucket_name=None, prefix_name=None):
        def share_prefix2users_statement(
                users, ac='ro', bucket_name=None, prefix_name=None, prefix4cond=None
            ):
            return cls(STATEMENT_TPL,
                principal = BP_principal.users([BP_principal.u2arn(t, u) for (t,u) in users]),
                action = BP_action.rmap(ac),
                resource = BP_resource.prefix(bucket_name, prefix_name) if prefix4cond is None
                    else BP_resource.list_condition(bucket_name),
                condition = None if prefix4cond is None else BP_condition.prefix(prefix4cond)
            )
        return [
            share_prefix2users_statement(users, ac, bucket_name, prefix_name),
            share_prefix2users_statement(users, 'li', bucket_name, prefix_name, prefix_name),
        ]

    @classmethod
    def prefix(cls, users=[], action=None, bucket_name=None, prefix_name=None):
        return [
            cls(STATEMENT_TPL,
                principal = BP_principal.users(users),
                action = action,
                resource = BP_resource.prefix(bucket_name, prefix_name)
            ),
            cls(STATEMENT_TPL,
                principal = BP_principal.users(users),
                action = BP_action.list(),
                resource = BP_resource.list_condition(bucket_name),
                condition = BP_condition.prefix(prefix_name)
            ),
        ]
