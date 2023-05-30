# -*- coding: utf-8 -*-

""" """

import pytest
from aws_plugin_bucket_policy.bucket_policy import BucketPolicy
from aws_plugin_bucket_policy.constants import *

@pytest.fixture(scope="function")
def bp():
    bp = BucketPolicy(test=True)
    return bp
