# -*- coding: utf-8 -*-
#

ACTION_RW = ['s3:ListBucket', 's3:GetObject', 's3:PutObject', 's3:DeleteObject']
ACTION_RO = ['s3:ListBucket', 's3:GetObject']
ACTION_LI = ['s3:ListBucket']
ACTION_ALL = 's3:*'

PRINCIPAL_PUBLIC = "*"
PRINCIPAL_AWS = { 'AWS': [] }
PRINCIPAL_USER = 'arn:aws:iam::{TENANT_NAME}:user/{USER_NAME}'
PRINCIPAL_TENANT = '{TENANT_NAME}'

RESOURCE_BUCKET = ['arn:aws:s3:::{BUCKET_NAME}', 'arn:aws:s3:::{BUCKET_NAME}/*']
RESOURCE_PREFIX = ['arn:aws:s3:::{BUCKET_NAME}/{PREFIX_NAME}', 'arn:aws:s3:::{BUCKET_NAME}/{PREFIX_NAME}/*']
RESOURCE_LIST_COND = ['arn:aws:s3:::{BUCKET_NAME}']
CONDITION_LIST = { "StringLike": { "s3:prefix": [ "{PREFIX_NAME}/*" ] }, "StringEquals": { "s3:delimiter": [ "/" ] } }

STATEMENT_TPL = { "Sid": "statement-{STATEMENT_ID}", "Effect": "Allow", "Principal": {}, "Action": [], "Resource": [] }

POLICY_TPL = { "Id": "policy-{POLICY_ID}", "Version": "2012-10-17", "Statement": [] }

W_NOBUCKETPOLICY = 50

MINERRID = 100
E_BUCKETSET = 100
