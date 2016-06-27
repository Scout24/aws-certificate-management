#!/usr/bin/env python

import json
import sys

bucket = sys.argv[1]
domain = sys.argv[2]

rule = {
    "Name": "postmaster",
    "Enabled": True,
    "Recipients": [ "postmaster@{0}".format(domain) ],
    "Actions": [{
        "S3Action": {
            "BucketName": bucket
        }
    }]
}

print(json.dumps(rule))