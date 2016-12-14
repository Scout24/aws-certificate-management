import unittest2

from aws_certificate_management import (cleanup, setup_certificate,
                                        cleanup_ses_rule_set)

WILDCARD_DOMAIN = '*.pro-test.wolke.is'
WWW_DOMAIN = 'www.pro-test.wolke.is'
ACM_ARN_PREFIX = 'arn:aws:acm:eu-west-1:'
ACM_ARN_PREFIX2 = 'arn:aws:acm:eu-central-1:'


class SetupCertificateTests(unittest2.TestCase):
    def tearDown(self):
        # Cleanup might run into a race condition, where items are added
        # to the bucket just before the bucket-stack should be deleted.
        # So just retry before really giving up.
        for attempt in 1, 2, 3:
            try:
                cleanup(self.domain, self.domain)
            except Exception:
                pass
            else:
                return

    def test_setup_certificate_called_twice_wildcard(self):
        self.domain = WILDCARD_DOMAIN

        with self.assertLogs(logger='aws-certificate-management', level='INFO') as cm:
            setup_certificate(self.domain, self.domain, 'eu-west-1')
            cleanup_ses_rule_set(self.domain)
            setup_certificate(self.domain, self.domain, 'eu-west-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)

    def test_setup_certificate_called_twice_www(self):
        self.domain = WWW_DOMAIN

        with self.assertLogs(logger='aws-certificate-management', level='INFO') as cm:
            setup_certificate(self.domain, self.domain, 'eu-west-1')
            cleanup_ses_rule_set(self.domain)
            setup_certificate(self.domain, self.domain, 'eu-west-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)

    def test_setup_certificate_different_regions(self):
        self.domain = WILDCARD_DOMAIN

        with self.assertLogs(level='INFO') as cm:
            setup_certificate(self.domain, self.domain, 'eu-west-1')
            cleanup_ses_rule_set(self.domain)
            setup_certificate(self.domain, self.domain, 'eu-central-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)
        self.assertIn(ACM_ARN_PREFIX2, logged_messages)


if __name__ == "__main__":
    unittest2.main()
