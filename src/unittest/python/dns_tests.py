import unittest2

from aws_certificate_management.configure_dns import (
        normalize_domain, get_stack_name, STACK_NAME_POSTFIX)


class DNSTests(unittest2.TestCase):
    def test_get_stack_name_removes_invalid_characters(self):
        stack_name = get_stack_name("foo-bar.invalid")
        self.assertEqual(stack_name, "foo-barinvalid" + STACK_NAME_POSTFIX)

    def test_normalize_domain_wildcard(self):
        self.assertEqual(normalize_domain("*.foo.bar"), "foo.bar")

    def test_normalize_domain_no_wildcard(self):
        self.assertEqual(normalize_domain("foo.bar"), "foo.bar")
