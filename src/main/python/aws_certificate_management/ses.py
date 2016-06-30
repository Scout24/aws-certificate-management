from __future__ import print_function, absolute_import, division

import json
import logging
import subprocess

def delete_rule_set(rule_set_name):
    """Delete the given rule set if it exists

    If the rule set is currently active (which would normally prevent
    deletion), the rule set is deactivated first.
    """
    # TODO: check if the rule is currently active

    command = ['aws', 'ses', 'delete-receipt-rule-set',
               '--rule-set-name', rule_set_name]
    logging.debug("Running this command: %r", command)
    subprocess.check_call(command)


def generate_rule(domain, s3_bucket):
    rule = {
        "Name": "postmaster",
        "Enabled": True,
        "Recipients": ["postmaster@{0}".format(domain)],
        "Actions": [{
            "S3Action": {
                "BucketName": s3_bucket
            }
        }]
    }
    return json.dumps(rule)


def create_rule_set(rule_set_name, rule):
    """Create the given rule set and activate it

    This assumes that no rule set of that name currently exists
    """
    command = ['aws', 'ses', 'create-receipt-rule-set',
               '--rule-set-name', rule_set_name]
    logging.debug("Running this command: %r", command)
    subprocess.check_call(command)

    command = ['aws', 'ses', 'create-receipt-rule',
               '--rule-set-name', rule_set_name, '--rule', rule]
    logging.debug("Running this command: %r", command)
    subprocess.check_call(command)

    command = ['aws', 'ses', 'set-active-receipt-rule-set',
               '--rule-set-name', rule_set_name]
    logging.debug("Running this command: %r", command)
    subprocess.check_call(command)


def setup_ses_rule_set(domain, s3_bucket):
    rule_set_name = "standard_addresses_for_{0}".format(domain)
    rule = generate_rule(domain, s3_bucket)

    delete_rule_set(rule_set_name)
    create_rule_set(rule_set_name, rule)
