import unittest2

from aws_certificate_management.configure_dns import create_ses_dns_records
import dns.resolver


class DNSTests(unittest2.TestCase):
    def xx_test_create_ses_dns_records(self):
        create_ses_dns_records("*.pro-test.wolke.is")

        answers = dns.resolver.query('pro-test.wolke.is', 'MX')
        self.assertEqual(answers[0], "10 inbound-smtp.eu-west-1.amazonaws.com.")


if __name__ == "__main__":
    unittest2.main()

