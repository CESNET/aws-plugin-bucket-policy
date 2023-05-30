# -*- coding: utf-8 -*-
#
"""
"""

import json, random, re
from copy import deepcopy
from datetime import datetime

from .constants import *
from .bp_classes import *

class BucketPolicy():
    def __init__(self, policy_str=None, test=False, debug=False, quiet=False):
        self._test = test
        self._debug = debug
        self._quiet = quiet
        self._json = None
        if policy_str == None: self.empty()
        elif policy_str != "": self.load(policy_str)

    def _get_date_rnd_suffix(self, test=False):
        if test: return "TEST"
        date = datetime.now().strftime('%y%m%d-%H%M%S')
        rand = random.randint(1000,9999)
        return f"{date}-{rand}"

    def empty(self):
        self._json = deepcopy(POLICY_TPL)
        pol_id = self._get_date_rnd_suffix(self._test)
        self._json['Id'] = self._json['Id'].format(POLICY_ID=pol_id)

    def _hex2char(self, matchobj):
        str = matchobj.group(1)
        return '%' if str=='%' else chr(int(str, 16))

    def _parse_spec(self, spec):
        #specregs = {'tenant':r'^[a-zA-Z0-9_]+$', 'user':r'^[-a-zA-Z0-9_\.]+$' , 'action':r'^(rw|ro|li|all)$'}
        specregs = {'tenant':r'^[a-zA-Z0-9_]+$', 'user':r'^[-a-zA-Z0-9_\.]+$' , 'action':r'^(rw|ro)$', 'prefix':f'^[-a-zA-Z0-9_/%]+$'}
        rv = []
        for it in (spec if isinstance(spec, list) else []):
            toks = [tok.split('=') for tok in it.split(',')]
            rv2 = {}
            for key,val in toks:
                if key not in specregs: raise Exception(f'Wrong spec key ({key})')
                if re.match(specregs[key], val): rv2[key] = val
                else: raise Exception(f'Wrong spec value ({val}) for key={key}')
                if key=='prefix': rv2[key] = re.sub(r'%([0-9a-f]{2}|%)', self._hex2char, rv2[key])
            rv.append(rv2)
        return rv

    def new_policy_ro_public(self, bn, type, spec, owner):
        # aws --profile $PROFILE s3bucket-policy new-policy --bucket $BUCKET --newpol-type ro-public
        self.add_statements(
            BP_statement.public_bucket_ro(bn),
        )

    def new_policy_share_w_user(self, bn, type, spec, owner):
        # aws --profile $PROFILE s3bucket-policy new-policy --bucket $BUCKET
        #			--newpol-type share-w-user --newpol-spec 'tenant=ten1,user=u1,action=rw'
        #			--newpol-type share-w-user --newpol-spec 'tenant=ten1,user=u1,action=rw' 'tenant=ten2,user=u2,action=ro' ...
        rw_users = [ [owner['tenant'],owner['user']] ]
        ro_users = []
        for specval in self._parse_spec(spec):
            tenant = specval['tenant'] if 'tenant' in specval and specval['tenant']!='' else owner['tenant']
            action = specval['action'] if 'action' in specval and specval['action']!='' else 'ro'
            if action == 'rw': rw_users.append([tenant,specval['user']])
            if action == 'ro': ro_users.append([tenant,specval['user']])
        statements = [
            BP_statement.share2users(rw_users, 'rw', bn),
        ]
        if len(ro_users)>0: statements.append(
            BP_statement.share2users(ro_users, 'ro', bn),
        )
        self.add_statements(statements)

    def new_policy_share_w_tenant(self, bn, type, spec, owner):
        # aws --profile $PROFILE s3bucket-policy new-policy --bucket $BUCKET
        #			--newpol-type share-w-tenant --newpol-spec 'tenant=tht,action=rw'
        owner_ok = False
        statements = []
        for specval in self._parse_spec(spec):
            tenant = specval['tenant'] if 'tenant' in specval and specval['tenant']!='' else owner['tenant']
            action = specval['action'] if 'action' in specval and specval['action']!='' else 'ro'
            if tenant == owner['tenant'] and action == 'rw': owner_ok = True
            statements.append(
                BP_statement.share2tenant(tenant, action, bn),
            )
        if not owner_ok:
            statements.insert(0,
                BP_statement.share2users([[owner['tenant'],owner['user']]], 'rw', bn),
            )
        self.add_statements(statements)

    def new_policy_share_prefix_w_user(self, bn, type, spec, owner):
        # aws --profile $PROFILE s3bucket-policy new-policy --bucket $BUCKET
        #			--newpol-type share-prefix-w-user --newpol-spec 'tenant=ten1,user=u1,action=rw,prefix=abc'
        #			--newpol-type share-prefix-w-user --newpol-spec 'tenant=ten1,user=u1,action=rw,prefix=abc' 'tenant=ten2,user=u2,action=ro,prefix=def' ...
        rw_p_users = {}
        ro_p_users = {}
        for specval in self._parse_spec(spec):
            tenant = specval['tenant'] if 'tenant' in specval and specval['tenant']!='' else owner['tenant']
            action = specval['action'] if 'action' in specval and specval['action']!='' else 'ro'
            prefix = specval['prefix'] if 'prefix' in specval and specval['prefix']!='' else ''
            if action == 'rw':
                if prefix not in rw_p_users: rw_p_users[prefix] = []
                rw_p_users[prefix].append([tenant,specval['user']])
            if action == 'ro':
                if prefix not in ro_p_users: ro_p_users[prefix] = []
                ro_p_users[prefix].append([tenant,specval['user']])
        statements = [
            BP_statement.share2users([[owner['tenant'],owner['user']]], 'rw', bn),
        ]
        for pref in rw_p_users:
            if len(rw_p_users[pref])>0: statements.append(
                BP_statement.share_prefix2users(rw_p_users[pref], 'rw', bn, pref),
            )
        for pref in ro_p_users:
            if len(ro_p_users[pref])>0: statements.append(
                BP_statement.share_prefix2users(ro_p_users[pref], 'ro', bn, pref),
            )
        self.add_statements(statements)

    def new_policy(self, bn, type, spec, owner):
        self.empty()
        handlers = {
            'ro-public': self.new_policy_ro_public,
            'share-w-user': self.new_policy_share_w_user,
            'share-w-tenant': self.new_policy_share_w_tenant,
            'share-prefix-w-user': self.new_policy_share_prefix_w_user,
        }
        if type in handlers:
            handlers[type](bn, type, spec, owner)
        else:
            raise Exception(f"Unknown newpol-type ({type})")

    def add_statement(self, principal={}, action=ACTION_RO, resource=[], condition=None):
        self.add_statements(
            BP_statement.general(
                principal = principal, action = action, resource = resource, condition=condition
            )
        )

    def add_statements(self, sts):
        sts = sts if isinstance(sts, list) else [sts, ]
        # flatten:
        sts = [v for w in sts for v in (w if isinstance(w, list) else [w, ])]
        for st in sts:
            st_id = self._get_date_rnd_suffix(self._test)
            st.set_id(st_id)
            self._json['Statement'].append(st.get())

    def get_statements(self):
        return self._json['Statement']

    def print_statement_list(self):
        for st in self.get_statements():
            principal = BP_principal.map(st['Principal'])
            action = BP_action.map(st['Action'])
            resource = BP_resource.map(st['Resource'] if 'Resource' in st else '')
            print(f"Statement: \"{st['Sid']}\" {principal}, {action}, {resource if resource!='' else 'Unspec.resource'}")

    def load(self, policy_str):
        self._json = json.loads(policy_str)

    def get_json(self):
        return self._json

    def save(self, indent=2):
        if self._json is None: return ""
        return json.dumps(self._json, indent=indent)

    def print(self, prefix='', suffix=''):
        policy = self.save()
        if self._quiet:
            print(policy)
        else:
            msg = f"\n{policy}" if self._json != None else "No policy defined"
            print(f"{prefix} policy: {msg}{suffix}")
        #bp.debug()

    def debug(self):
        for st in  self._json['Statement']:
            print(f"{st['Sid']}:")
            print("  ", st['Principal'])
            print("  ", st['Action'])
            print("  ", st['Resource'])

#__all__ = ('BucketPolicy', 'BP_statement', 'BP_principal', 'BP_action', 'BP_resource', 'BP_condition')
