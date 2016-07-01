from __future__ import print_function, absolute_import, division

import subprocess
import time
import unittest2

from aws_certificate_management.ses import (
        delete_rule_set, generate_rule, create_rule_set, get_active_rule_set)


class SESTests(unittest2.TestCase):
    def setUp(self):
        # Calls to "aws ses set-active-receipt-rule-set..." are thottled to
        # one per second.
        time.sleep(1)

        self.rule_set_name = "integrationtest_for_aws_certificate_management"
        self.s3_bucket = "integration-tests-for-aws-certificate-management"
        self.rule = generate_rule("somedomain.invalid", self.s3_bucket)

        delete_rule_set(self.rule_set_name)

    def test_create_delete_rule_set(self):
        try:
            create_rule_set(self.rule_set_name, self.rule)

            # This fails if the rule does not actually exist
            subprocess.check_call(["aws", "ses", "describe-receipt-rule-set",
                                  "--rule-set-name", self.rule_set_name])
            self.assertEqual(self.rule_set_name, get_active_rule_set())
        finally:
            delete_rule_set(self.rule_set_name)

        # Since the rule should be deleted now, this should fail:
        self.assertRaises(Exception, subprocess.check_call,
                          ["aws", "ses", "describe-receipt-rule-set",
                          "--rule-set-name", self.rule_set_name])


if __name__ == "__main__":
    unittest2.main()

