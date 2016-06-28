#!/usr/bin/env bash

# Some sets to write better scripts ;)
set -o errexit  # Exit on error
set -o nounset  # Trigger error when expanding unset variables

function usage()
{
    cat <<-HEREDOC
	Usage: $0 domain
	domain  - The domain name to get a certificate for (e.g. www.foo.com or "*.foo.com")
HEREDOC
    exit 0
}

VERBOSE=1

# parse domain argument
[[ $# != 1 ]] && usage
domain=$1

function debug()
{
    [[ ${VERBOSE} ]] && echo $1
}

function get_domain()
{
    subdomain=${domain%%.*}
    if [[ $subdomain == '*' || $subdomain == 'www' ]]
    then
        domain=${domain#*.}
        debug "truncate to domain: $domain"
    fi
}

function create_ses_stack()
{
    txt_token=$(aws ses verify-domain-identity --domain ${domain} | jq -r '.VerificationToken')
    dkim_tokens=$(aws ses verify-domain-dkim --domain ${domain})
    dkim_token_one=$(echo ${dkim_tokens} | jq -r '.DkimTokens[0]')
    dkim_token_two=$(echo ${dkim_tokens} | jq -r '.DkimTokens[1]')
    dkim_token_three=$(echo ${dkim_tokens} | jq -r '.DkimTokens[2]')

    cf sync -c src/main/cfn/ses-receive-domain-validation-mails.yaml \
	-p ses-dns-recordset.dnsBaseName=${domain}.    \
	-p ses-dns-recordset.dkimOne=${dkim_token_one}   \
	-p ses-dns-recordset.dkimTwo=${dkim_token_two}   \
	-p ses-dns-recordset.dkimThree=${dkim_token_three} \
	-p ses-dns-recordset.verifyTxt=${txt_token}
}

function create_rule()
{
    bucket_name=$(aws cloudformation describe-stacks --stack-name email-bucket | jq -r '.Stacks[0].Outputs[0].OutputValue')

    ruleset_name="standard_addresses_for_${domain}"
    rule=$(./generate_ses_receipt_rule.py $bucket_name $domain)

    aws ses delete-receipt-rule-set --rule-set-name $ruleset_name
    aws ses create-receipt-rule-set --rule-set-name $ruleset_name
    aws ses create-receipt-rule --rule-set-name $ruleset_name --rule "$rule"
    aws ses set-active-receipt-rule-set --rule-set-name $ruleset_name
}

get_domain
echo $domain
# TODO rest

# final step is to call
# aws acm request-certificate --domain-name '*.foo.wolke.is'
