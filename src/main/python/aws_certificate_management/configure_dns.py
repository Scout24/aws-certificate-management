from __future__ import print_function, absolute_import, division

import os
from cfn_sphere import StackActionHandler
from cfn_sphere.stack_configuration import Config

import boto3

def create_ses_dns_records(domain, region='eu-west-1'):
    ses = boto3.client('ses')
    domain_identity = ses.verify_domain_identity(Domain=domain)
    verification_token = domain_identity['VerificationToken']

    dkim_tokens = ses.verify_domain_dkim(Domain=domain)

    template = "{0}../../../src/main/cfn/templates/recordset.json"\
        .format(os.path.abspath(os.path.dirname(__file__)))

    StackActionHandler(config=Config(config_dict={
        'region': region,
        'stacks': {
            "{0}-ses-dns-records".format(domain): {
                'template-url': template
            }
        }
    })).create_or_update_stacks()
