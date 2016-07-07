#!/usr/bin/env cram
# vim: set syntax=cram :


  $ aws-certificate-management --help
  usage: aws-certificate-management [-h] [-v] [-q] [--region REGION] [-c] domain
  
  Tool to create AWS certificates
  
  positional arguments:
    domain           For which domain you need a certificate. Can also be a
                     wildcard like "*.foo.bar"
  
  optional arguments:
    -h, --help       show this help message and exit
    -v, --verbose
    -q, --quiet
    --region REGION  For which region the certificate is created (default is eu-
                     west-1)
    -c, --cleanup    Clean up stacks and resources that are only needed to
                     request the certificate

Missing "domain" parameter
  $ aws-certificate-management --cleanup
  usage: aws-certificate-management [-h] [-v] [-q] [--region REGION] [-c] domain
  aws-certificate-management: error: too few arguments
  [2]

  $ aws-certificate-management
  usage: aws-certificate-management [-h] [-v] [-q] [--region REGION] [-c] domain
  aws-certificate-management: error: too few arguments
  [2]
