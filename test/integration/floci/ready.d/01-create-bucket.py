#!/usr/bin/env python3
# Floci init "ready" hook (see https://floci.io/floci/configuration/initialization-hooks/):
# runs inside the Floci container once its S3 service is up. Unlike some
# other local S3 mocks, Floci does not auto-create buckets on first request,
# so the webapp/workers would otherwise hit NoSuchBucket on every upload.
import os
import boto3
from botocore.exceptions import ClientError

bucket_name = os.environ.get("AWS_S3_BUCKET", "flir-conservator-development")
s3 = boto3.client("s3")

try:
    s3.create_bucket(Bucket=bucket_name)
    print(f"created bucket {bucket_name}")
except ClientError as e:
    if e.response["Error"]["Code"] not in (
        "BucketAlreadyExists",
        "BucketAlreadyOwnedByYou",
    ):
        raise
    print(f"bucket {bucket_name} already exists")

s3.put_bucket_cors(
    Bucket=bucket_name,
    CORSConfiguration={
        "CORSRules": [
            {
                "AllowedOrigins": ["*"],
                "AllowedMethods": ["GET", "PUT"],
                "AllowedHeaders": ["*"],
                "ExposeHeaders": ["ETag"],
                "MaxAgeSeconds": 3000,
            }
        ]
    },
)
print(f"configured CORS on bucket {bucket_name}")
