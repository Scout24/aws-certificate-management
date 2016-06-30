import unittest2
import random

from aws_certificate_management.ses import delete_rule_set, generate_rule, create_rule_set


class SESTests(unittest2.TestCase):
    def test_delete_rule_set(self):
        rule_set_name = "integrationtest_for_aws_certificate_management"
        s3_bucket = "integration-tests-for-aws-certificate-management"
        rule = generate_rule("some_domain.invalid", s3_bucket)

        create_rule_set(rule_set_name, rule)
        delete_rule_set(rule_set_name)




if __name__ == "__main__":
    unittest2.main()

