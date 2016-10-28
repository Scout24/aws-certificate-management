import unittest2

from aws_certificate_management.configure_dns import (
        normalize_domain, normalize_hosted_zone, get_dns_stack_name, DNS_STACK_NAME_POSTFIX,
        get_bucket_stack_name, BUCKET_STACK_NAME_POSTFIX,
        get_stack_action_handler)


class DNSTests(unittest2.TestCase):
    def test_get_dns_stack_name_removes_invalid_characters(self):
        stack_name = get_dns_stack_name("foo-bar.invalid")
        self.assertEqual(stack_name, "foo-barinvalid" + DNS_STACK_NAME_POSTFIX)

    def test_get_bucket_stack_name_removes_invalid_characters(self):
        stack_name = get_bucket_stack_name("foo-bar.invalid")
        self.assertEqual(stack_name, "foo-barinvalid" + BUCKET_STACK_NAME_POSTFIX)

    def test_normalize_domain_wildcard(self):
        self.assertEqual(normalize_domain("*.foo.bar"), "foo.bar")

    def test_normalize_domain_www(self):
        self.assertEqual(normalize_domain("www.foo.bar"), "foo.bar")

    def test_normalize_domain_no_wildcard(self):
        self.assertEqual(normalize_domain("foo.bar"), "foo.bar")

    def test_normalize_hosted_zone_wildcard(self):
        self.assertEqual(normalize_hosted_zone("*.foo.bar"), "foo.bar.")

    def test_normalize_hosted_zone_www(self):
        self.assertEqual(normalize_hosted_zone("www.foo.bar"), "foo.bar.")

    def test_normalize_hosted_zone_no_wildcard(self):
        self.assertEqual(normalize_hosted_zone("foo.bar"), "foo.bar.")

    def test_normalize_hosted_zone_no_dot(self):
        self.assertEqual(normalize_hosted_zone("foo.bar"), "foo.bar.")

    def test_get_stack_action_handler_no_tokens(self):
        handler = get_stack_action_handler('*.foo.invalid', '*.foo.invalid.')
        self.assertIsInstance(handler, object)

    def test_get_stack_action_handler_no_tokens_separate_hz(self):
        handler = get_stack_action_handler('*.foo.invalid', 'foo.invalid.')
        self.assertIsInstance(handler, object)

    def test_get_stack_action_handler_no_tokens_different_hz(self):
        handler = get_stack_action_handler('*.foo.bar.invalid', 'bar.invalid.')
        self.assertIsInstance(handler, object)

    def test_get_stack_action_handler_with_tokens(self):
        handler = get_stack_action_handler(
            '*.foo.invalid', 'foo.invalid.', 'verification_token', ['dkim1', 'dkim2', 'dkim3'])
        self.assertIsInstance(handler, object)
