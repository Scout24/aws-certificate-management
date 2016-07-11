from __future__ import print_function, absolute_import, division

import os

from .ses import setup_ses_rule_set, cleanup_ses_rule_set
from .configure_dns import create_ses_dns_records
from .configure_dns import delete_ses_dns_records_and_bucket


__all__ = ["setup_ses_rule_set", "create_ses_dns_records",
           "delete_ses_dns_records_and_bucket", "cleanup_ses_rule_set",
           "setup_certificate", "cleanup"]


def setup_certificate(domain, region):
    mail_bucket_name = create_ses_dns_records(domain)
    setup_ses_rule_set(domain, mail_bucket_name)

    request_certificate = "aws acm request-certificate --domain-name '{domain}' --region='{region}'"
    os.system(request_certificate.format(domain=domain, region=region))


def cleanup(domain):
    delete_ses_dns_records_and_bucket(domain)
    cleanup_ses_rule_set(domain)
