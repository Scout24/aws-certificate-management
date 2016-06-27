#!/usr/bin/env bash

set -x -e

domain='foo.wolke.is'

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

bucket_name=$(aws cloudformation describe-stacks --stack-name email-bucket | jq -r '.Stacks[0].Outputs[0].OutputValue')

ruleset_name="standard_addresses_for_${domain}"
rule=$(./generate_ses_receipt_rule.py $bucket_name $domain)

aws ses delete-receipt-rule-set --rule-set-name $ruleset_name
aws ses create-receipt-rule-set --rule-set-name $ruleset_name
aws ses create-receipt-rule --rule-set-name $ruleset_name --rule "$rule"
aws ses set-active-receipt-rule-set --rule-set-name $ruleset_name


# final step is to call
# aws acm request-certificate --domain-name '*.foo.wolke.is'
