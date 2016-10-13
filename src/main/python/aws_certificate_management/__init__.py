from __future__ import print_function, absolute_import, division

import boto3
import logging

from .ses import setup_ses_rule_set, cleanup_ses_rule_set
from .configure_dns import create_ses_dns_records
from .configure_dns import delete_ses_dns_records_and_bucket


__all__ = ["setup_ses_rule_set", "create_ses_dns_records",
           "delete_ses_dns_records_and_bucket", "cleanup_ses_rule_set",
           "setup_certificate", "cleanup"]


def setup_certificate(domain, hosted_zone, region):
    mail_bucket_name = create_ses_dns_records(domain, hosted_zone)
    setup_ses_rule_set(domain, mail_bucket_name)

    client = boto3.client('acm', region_name=region)
    response = client.request_certificate(DomainName=domain)
    certificate_arn = response['CertificateArn']
    logging.getLogger('aws-certificate-management').info(
        "Your certificate ARN is %r", certificate_arn)


def cleanup(domain, hosted_zone):
    delete_ses_dns_records_and_bucket(domain, hosted_zone)
    cleanup_ses_rule_set(domain)
