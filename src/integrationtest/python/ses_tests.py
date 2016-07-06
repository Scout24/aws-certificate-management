from __future__ import print_function, absolute_import, division

import boto3
import json
import random
import subprocess
import sys
import time
import unittest2

from aws_certificate_management.ses import (
        delete_rule_set, generate_rule, create_rule_set, get_active_rule_set,
        REGION, setup_ses_rule_set)
from aws_certificate_management.configure_dns import delete_items_in_bucket

# FIXME: Don't build for Python 2.6 instead of skipping the test
@unittest2.skipIf(sys.version_info < (2,7), "Python 2.6 has no check_output")
class SESTests(unittest2.TestCase):
    @classmethod
    def setup_bucket_policy(cls):
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        policy_document = {
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Sid": "GiveSESPermissionToWriteEmail",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ses.amazonaws.com"
                    },
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::{0}/*".format(cls.s3_bucket),
                    "Condition": {
                        "StringEquals": {
                            "aws:Referer": account_id
                        }
                    }
                }
            ]
        }
        s3 = boto3.resource('s3')
        policy = s3.BucketPolicy(cls.s3_bucket)
        policy.put(Policy=json.dumps(policy_document))

    @classmethod
    def setUpClass(cls):
        cls.s3_client = boto3.client('s3')
        cls.s3_bucket = "aws-certificate-management-tests"
        cls.s3_bucket += str(random.randint(0, 2**64))

        cls.s3_client.create_bucket(Bucket=cls.s3_bucket, CreateBucketConfiguration={
                'LocationConstraint': 'EU'})
        cls.setup_bucket_policy()

    @classmethod
    def tearDownClass(cls):
        delete_items_in_bucket(cls.s3_bucket)
        cls.s3_client.delete_bucket(Bucket=cls.s3_bucket)

    def setUp(self):
        # Calls to "aws ses set-active-receipt-rule-set..." are throttled to
        # one per second.
        time.sleep(1)

        self.rule_set_name = "integrationtest_for_aws_certificate_management"
        self.rule = generate_rule("somedomain.invalid", self.s3_bucket)

        delete_rule_set(self.rule_set_name)

    def test_create_delete_rule_set(self):
        try:
            create_rule_set(self.rule_set_name, self.rule)

            # This fails if the rule does not actually exist
            subprocess.check_call(["aws", "ses", "describe-receipt-rule-set",
                                  "--rule-set-name", self.rule_set_name,
                                  REGION])
            self.assertEqual(self.rule_set_name, get_active_rule_set())
        finally:
            delete_rule_set(self.rule_set_name)

        # Since the rule should be deleted now, this should fail:
        self.assertRaises(Exception, subprocess.check_call,
                          ["aws", "ses", "describe-receipt-rule-set",
                          "--rule-set-name", self.rule_set_name,
                          REGION])

    def test_setup_ses_rule_set(self):
        try:
            setup_ses_rule_set("*.pro-test.wolke.is", self.s3_bucket)
        finally:
            delete_rule_set(self.rule_set_name)


if __name__ == "__main__":
    unittest2.main()

