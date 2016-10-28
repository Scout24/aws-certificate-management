import unittest2

from aws_certificate_management import cleanup, setup_certificate

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
                cleanup(WILDCARD_DOMAIN)
            except Exception:
                pass
            else:
                return

    def test_setup_certificate_called_twice_wildcard(self):
        with self.assertLogs(logger='aws-certificate-management', level='INFO') as cm:
            setup_certificate(WILDCARD_DOMAIN, WILDCARD_DOMAIN, 'eu-west-1')
            setup_certificate(WILDCARD_DOMAIN, WILDCARD_DOMAIN, 'eu-west-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)

    def test_setup_certificate_called_twice_www(self):
        with self.assertLogs(logger='aws-certificate-management', level='INFO') as cm:
            setup_certificate(WWW_DOMAIN, WWW_DOMAIN, 'eu-west-1')
            setup_certificate(WWW_DOMAIN, WWW_DOMAIN, 'eu-west-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)

    def test_setup_certificate_different_regions(self):
        with self.assertLogs(level='INFO') as cm:
            setup_certificate(WILDCARD_DOMAIN, WILDCARD_DOMAIN, 'eu-west-1')
            setup_certificate(WILDCARD_DOMAIN, WILDCARD_DOMAIN, 'eu-central-1')

        logged_messages = "".join(cm.output)
        self.assertIn(ACM_ARN_PREFIX, logged_messages)
        self.assertIn(ACM_ARN_PREFIX2, logged_messages)
        




if __name__ == "__main__":
    unittest2.main()
