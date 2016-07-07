import unittest2

from aws_certificate_management.configure_dns import create_ses_dns_records, delete_ses_dns_records
import dns.resolver


class DNSTests(unittest2.TestCase):
    def test_create_ses_dns_records_wildcard(self):
        try:
            create_ses_dns_records("*.pro-test.wolke.is")

            answers = dns.resolver.query('pro-test.wolke.is', 'MX')
            self.assertEqual(str(answers[0]), "10 inbound-smtp.eu-west-1.amazonaws.com.")
        finally:
            delete_ses_dns_records("*.pro-test.wolke.is")

    def test_create_ses_dns_records_for_www(self):
        try:
            create_ses_dns_records("www.pro-test.wolke.is")

            answers = dns.resolver.query('pro-test.wolke.is', 'MX')
            self.assertEqual(str(answers[0]), "10 inbound-smtp.eu-west-1.amazonaws.com.")
        finally:
            delete_ses_dns_records("www.pro-test.wolke.is")


if __name__ == "__main__":
    unittest2.main()

