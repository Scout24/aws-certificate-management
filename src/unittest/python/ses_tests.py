from __future__ import print_function, absolute_import, division

import json
import unittest2

from aws_certificate_management.ses import generate_rule

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
