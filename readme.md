AWS Certificate Management
==========================

[![Travis build status image](https://travis-ci.org/ImmobilienScout24/aws-certificate-management.png?branch=master "Travis build status")](https://travis-ci.org/ImmobilienScout24/aws-certificate-management)
[![Coverage Status](https://coveralls.io/repos/github/ImmobilienScout24/aws-certificate-management/badge.svg?branch=master)](https://coveralls.io/github/ImmobilienScout24/aws-certificate-management?branch=master)
[![Code Health](https://landscape.io/github/ImmobilienScout24/aws-certificate-management/master/landscape.svg?style=flat "Coverage status")](https://landscape.io/github/ImmobilienScout24/aws-certificate-management/master)
[![Version](https://img.shields.io/pypi/v/aws-certificate-management.svg "Version")](https://pypi.python.org/pypi/aws-certificate-management)

About
=====

This project helps you to (semi automatic) setup a certificate for your domain in your AWS account.
It uses cloudformation (cfn-sphere) and the AWS Certificate Manager.

Project is in the early stage of development ...

Side Effects
------------

This script will deactivate the active rule set in SES! You have to activate your old rule set by hand, if needed.
