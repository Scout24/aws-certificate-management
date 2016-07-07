from __future__ import print_function, absolute_import, division

import logging
import os
import re
from cfn_sphere import StackActionHandler
from cfn_sphere.stack_configuration import Config

import boto3

DNS_STACK_NAME_POSTFIX = "-ses-dns-records"
BUCKET_STACK_NAME_POSTFIX = "-email-bucket"


def prepare_domain(domain):
    # Stack names in CFN-sphere may not contain anything but letters,
    # numbers and "-".
    return re.sub("[^-a-zA-Z0-9]", "", domain)


def get_dns_stack_name(domain):
    return prepare_domain(domain) + DNS_STACK_NAME_POSTFIX


def get_bucket_stack_name(domain):
    return prepare_domain(domain) + BUCKET_STACK_NAME_POSTFIX


def get_stack_action_handler(domain, region, verification_token=None, dkim_tokens=None):
    ses_dns_template = "{0}/../../../../src/main/cfn/templates/recordset.json"
    ses_dns_template = ses_dns_template.format(os.path.abspath(os.path.dirname(__file__)))
    verification_token = verification_token or ""
    dkim_tokens = dkim_tokens or ["", "", ""]

    mail_bucket_template = "{0}/../../../../src/main/cfn/templates/ses-email-receiving-bucket.json"
    mail_bucket_template = mail_bucket_template.format(os.path.abspath(os.path.dirname(__file__)))

    return StackActionHandler(config=Config(config_dict={
        'region': region,
        'stacks': {
            get_dns_stack_name(domain): {
                'template-url': ses_dns_template,
                'parameters': {
                    'dnsBaseName': domain + ".",
                    'dkimOne': dkim_tokens[0],
                    'dkimTwo': dkim_tokens[1],
                    'dkimThree': dkim_tokens[2],
                    'verifyTxt': verification_token
                }
            },
            get_bucket_stack_name(domain): {
                'template-url': mail_bucket_template,
            }
        }
    }))


def normalize_domain(domain):
    if domain.startswith("*."):
        return domain[2:]
    return domain


def create_ses_dns_records(domain, region='eu-west-1'):
    logging.info("Creating DNS records to configure e-mail for your domain")
    domain = normalize_domain(domain)
    ses = boto3.client('ses', region_name=region)
    domain_identity = ses.verify_domain_identity(Domain=domain)
    verification_token = domain_identity['VerificationToken']
    dkim_tokens = ses.verify_domain_dkim(Domain=domain)['DkimTokens']

    stack_handler = get_stack_action_handler(domain, region, verification_token, dkim_tokens)
    logging.info("Creating CFN stacks %s and %s",
                 get_dns_stack_name(domain), get_bucket_stack_name(domain))
    stack_handler.create_or_update_stacks()

    stack_outputs = stack_handler.cfn.get_stack_outputs()
    s3_bucket_for_mail = stack_outputs[get_bucket_stack_name(domain)]['bucketName']
    logging.info("Mail for postmaster@<yourdomain> is delivered to "
                 "S3 bucket %s", s3_bucket_for_mail)
    return s3_bucket_for_mail


def delete_items_in_bucket(s3_bucket):
    s3_client = boto3.client('s3')
    for item in s3_client.list_objects(Bucket=s3_bucket).get('Contents', []):
        s3_client.delete_object(Key=item['Key'], Bucket=s3_bucket)


def delete_ses_dns_records(domain, region='eu-west-1'):
    logging.info("Deleting DNS records that configure e-mail for your domain")
    domain = normalize_domain(domain)
    stack_handler = get_stack_action_handler(domain, region)

    stacks_dict = stack_handler.cfn.get_stack_outputs()
    bucket_stack_outputs = stacks_dict[get_bucket_stack_name(domain)]
    bucket_name = bucket_stack_outputs['bucketName']
    logging.info("Deleting all items in S3 bucket %r to prepare stack deletion", bucket_name)
    delete_items_in_bucket(bucket_name)

    stack_handler.delete_stacks()
    logging.info("Deletion of DNS records complete")
