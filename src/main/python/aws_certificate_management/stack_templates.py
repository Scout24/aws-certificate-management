RECORDSET_STACK = br"""
{
  "Description": "Route53 record sets to use SES to receive mail for a domain",
  "Parameters": {
    "dnsBaseName": {
      "Type": "String",
      "Description": "The name of the domain. You must specify a fully qualified domain name that ends with a period as the last label indication. If you omit the final period, AWS CloudFormation adds it."
    },
    "targetHostedZoneName": {
      "Type": "String",
      "Description": "The name of the hosted zone that holds the domain."
    },
    "dkimOne": {
      "Type": "String",
      "Description": "sub domain value for '.dkim.amazonses.com.' CNAME record"
    },
    "dkimTwo": {
      "Type": "String",
      "Description": "sub domain value for '.dkim.amazonses.com.' CNAME record"
    },
    "dkimThree": {
      "Type": "String",
      "Description": "sub domain value for '.dkim.amazonses.com.' CNAME record"
    },
    "verifyTxt": {
      "Type": "String",
      "Description": "verify domain TXT record value"
    }
  },
  "AWSTemplateFormatVersion": "2010-09-09",
  "Resources": {
    "mxDnsRecord": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "MX",
        "Name": {
          "Ref": "dnsBaseName"
        },
        "ResourceRecords": [
          "10 inbound-smtp.eu-west-1.amazonaws.com."
        ]
      }
    },
    "dkimDnsRecordThree": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "CNAME",
        "Name": {
          "Fn::Join": [
            ".",
            [
              {
                "Ref": "dkimThree"
              },
              "_domainkey",
              {
                "Ref": "dnsBaseName"
              }
            ]
          ]
        },
        "ResourceRecords": [
          {
            "Fn::Join": [
              "",
              [
                {
                  "Ref": "dkimThree"
                },
                ".dkim.amazonses.com."
              ]
            ]
          }
        ]
      }
    },
    "dkimDnsRecordOne": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "CNAME",
        "Name": {
          "Fn::Join": [
            ".",
            [
              {
                "Ref": "dkimOne"
              },
              "_domainkey",
              {
                "Ref": "dnsBaseName"
              }
            ]
          ]
        },
        "ResourceRecords": [
          {
            "Fn::Join": [
              "",
              [
                {
                  "Ref": "dkimOne"
                },
                ".dkim.amazonses.com."
              ]
            ]
          }
        ]
      }
    },
    "verifyDomainDnsRecord": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "TXT",
        "Name": {
          "Fn::Join": [
            ".",
            [
              "_amazonses",
              {
                "Ref": "dnsBaseName"
              }
            ]
          ]
        },
        "ResourceRecords": [
          {
            "Fn::Join": [
              "",
              [
                "\"",
                {
                  "Ref": "verifyTxt"
                },
                "\""
              ]
            ]
          }
        ]
      }
    },
    "autodiscoverDnsRecord": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "CNAME",
        "Name": {
          "Fn::Join": [
            ".",
            [
              "autodiscover",
              {
                "Ref": "dnsBaseName"
              }
            ]
          ]
        },
        "ResourceRecords": [
          "autodiscover.mail.eu-west-1.awsapps.com."
        ]
      }
    },
    "dkimDnsRecordTwo": {
      "Type": "AWS::Route53::RecordSet",
      "Properties": {
        "HostedZoneName": {
          "Ref": "targetHostedZoneName"
        },
        "TTL": "900",
        "Type": "CNAME",
        "Name": {
          "Fn::Join": [
            ".",
            [
              {
                "Ref": "dkimTwo"
              },
              "_domainkey",
              {
                "Ref": "dnsBaseName"
              }
            ]
          ]
        },
        "ResourceRecords": [
          {
            "Fn::Join": [
              "",
              [
                {
                  "Ref": "dkimTwo"
                },
                ".dkim.amazonses.com."
              ]
            ]
          }
        ]
      }
    }
  }
}
"""

SES_EMAIL_BUCKET_STACK = b"""
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Destination bucket for emails received by SES",
  "Resources": {
    "bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "LifecycleConfiguration": {
          "Rules": [
            {
              "Status": "Enabled",
              "ExpirationInDays": 14
            }
          ]
        }
      }
    },
    "bucketPolicy": {
      "Type": "AWS::S3::BucketPolicy",
      "Properties": {
        "Bucket": {
          "Ref": "bucket"
        },
        "PolicyDocument": {
          "Statement": {
            "Sid": "GiveSESPermissionToWriteEmail",
            "Effect": "Allow",
            "Principal": {
              "Service": [
                "ses.amazonaws.com"
              ]
            },
            "Action": [
              "s3:PutObject"
            ],
            "Resource": {
              "Fn::Join": [
                "",
                [
                  "arn:aws:s3:::",
                  {
                    "Ref": "bucket"
                  },
                  "/*"
                ]
              ]
            },
            "Condition": {
              "StringEquals": {
                "aws:Referer": {
                  "Ref": "AWS::AccountId"
                }
              }
            }
          }
        }
      }
    }
  },
  "Outputs": {
    "bucketName": {
      "Value": { "Ref": "bucket" },
      "Description": "Name of the bucket where SES delivers mail to"
    }
  }
}
"""
