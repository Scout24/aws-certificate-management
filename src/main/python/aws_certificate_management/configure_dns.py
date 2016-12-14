from __future__ import print_function, absolute_import, division

import logging
import re
from tempfile import NamedTemporaryFile

import boto3
from cfn_sphere import StackActionHandler
from cfn_sphere.stack_configuration import Config
from pils import retry

from .stack_templates import RECORDSET_STACK, SES_EMAIL_BUCKET_STACK

LOGGER = logging.getLogger("aws-certificate-management")
DNS_STACK_NAME_POSTFIX = "-ses-dns-records"
BUCKET_STACK_NAME_POSTFIX = "-email-bucket"
REGION = "eu-west-1"

# These files will be closed (and deleted) when Python terminates.
recordset_template = NamedTemporaryFile(suffix=".json")
ses_template = NamedTemporaryFile(suffix=".json")
recordset_template.write(RECORDSET_STACK)
recordset_template.flush()
ses_template.write(SES_EMAIL_BUCKET_STACK)
ses_template.flush()


def prepare_domain(domain):
    # Stack names in CFN-sphere may not contain anything but letters,
    # numbers and "-".
    return re.sub("[^-a-zA-Z0-9]", "", domain)


def get_dns_stack_name(domain):
    return prepare_domain(domain) + DNS_STACK_NAME_POSTFIX


def get_bucket_stack_name(domain):
    return prepare_domain(domain) + BUCKET_STACK_NAME_POSTFIX


def get_stack_action_handler(domain, hosted_zone, verification_token=None, dkim_tokens=None):
    verification_token = verification_token or ""
    dkim_tokens = dkim_tokens or ["", "", ""]

    return StackActionHandler(config=Config(config_dict={
        'region': REGION,
        'stacks': {
            get_dns_stack_name(domain): {
                'template-url': recordset_template.name,
                'parameters': {
                    'dnsBaseName': domain + ".",
                    'targetHostedZoneName': hosted_zone,
                    'dkimOne': dkim_tokens[0],
                    'dkimTwo': dkim_tokens[1],
                    'dkimThree': dkim_tokens[2],
                    'verifyTxt': verification_token
                }
            },
            get_bucket_stack_name(domain): {
                'template-url': ses_template.name,
            }
        }
    }))


def normalize_domain(domain):
    if domain.startswith("*."):
        return domain[2:]
    elif domain.startswith("www."):
        return domain[4:]
    return domain


def normalize_hosted_zone(hosted_zone):
    if hosted_zone.startswith("*."):
        hosted_zone = hosted_zone[2:]
    elif hosted_zone.startswith("www."):
        hosted_zone = hosted_zone[4:]
    return hosted_zone if hosted_zone.endswith(".") else hosted_zone + "."


def create_ses_dns_records(domain, hosted_zone):
    LOGGER.info("Creating DNS records to configure e-mail for your domain")
    domain = normalize_domain(domain)
    hosted_zone = normalize_hosted_zone(hosted_zone)
    ses = boto3.client('ses', region_name=REGION)
    domain_identity = ses.verify_domain_identity(Domain=domain)
    verification_token = domain_identity['VerificationToken']
    dkim_tokens = ses.verify_domain_dkim(Domain=domain)['DkimTokens']

    stack_handler = get_stack_action_handler(domain, hosted_zone, verification_token, dkim_tokens)
    LOGGER.info("Creating CFN stacks %s and %s",
                get_dns_stack_name(domain), get_bucket_stack_name(domain))
    stack_handler.create_or_update_stacks()

    stack_outputs = stack_handler.cfn.get_stacks_outputs()
    s3_bucket_for_mail = stack_outputs[get_bucket_stack_name(domain)]['bucketName']
    LOGGER.info("Mail for postmaster@<yourdomain> will be delivered to "
                "S3 bucket %s", s3_bucket_for_mail)
    return s3_bucket_for_mail


def delete_items_in_bucket(s3_bucket):
    s3_client = boto3.client('s3')
    for item in s3_client.list_objects(Bucket=s3_bucket).get('Contents', []):
        s3_client.delete_object(Key=item['Key'], Bucket=s3_bucket)


def delete_ses_dns_records_and_bucket(domain, hosted_zone):
    LOGGER.info("Deleting DNS records that configure e-mail for your domain")
    domain = normalize_domain(domain)
    hosted_zone = normalize_hosted_zone(hosted_zone)
    stack_handler = get_stack_action_handler(domain, hosted_zone)

    stacks_dict = stack_handler.cfn.get_stacks_outputs()
    bucket_stack_outputs = stacks_dict[get_bucket_stack_name(domain)]
    bucket_name = bucket_stack_outputs['bucketName']
    LOGGER.info("Deleting all items in S3 bucket %r to prepare stack deletion",
                bucket_name)
    delete_items_in_bucket(bucket_name)

    retry(delay=10)(stack_handler.delete_stacks)()
    LOGGER.info("Deletion of DNS records and mail bucket complete")
