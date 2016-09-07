from __future__ import print_function, absolute_import, division

import json
import unittest2

from aws_certificate_management.ses import generate_rule, run, get_rule_set_name

class SESTests(unittest2.TestCase):

    def test_generate_rule(self):
        domain = "my.domain.invalid"
        s3_bucket = "bucketname"
        expected_rule = {
            "Name": "postmaster",
            "Enabled": True,
            "Recipients": ["postmaster@" + domain],
            "Actions": [{
                "S3Action": {
                    "BucketName": s3_bucket
                }
            }]
        }

        rule = generate_rule(domain, s3_bucket)
        self.assertEqual(expected_rule, json.loads(rule))

    def test_run__command_successful(self):
        with self.assertLogs("aws-certificate-management", level="DEBUG"):
            run(['true'])

    def test_run__command_fails(self):
        with self.assertLogs("aws-certificate-management", level="DEBUG"):
            self.assertRaises(Exception, run, ['false'])

    def test_get_rule_set_name(self):
        name = get_rule_set_name('foo')
        self.assertTrue(name.startswith("tmp_rule_acm_"))

    def test_get_rule_set_name_long_domain(self):
        # rule name contains less than 64 characters.
        # ee: http://boto3.readthedocs.io/en/latest/reference/services/ses.html?highlight=ses#SES.Client.create_receipt_rule
        long_domain_name = 'foo' + 'o' * 64
        name = get_rule_set_name(long_domain_name)
        self.assertTrue(len(name) < 64)
        self.assertTrue(name.startswith('tmp_rule_acm_'))

