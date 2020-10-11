#!/bin/bash


source ../../venv/bin/activate

read -p "API Key: " key
read -p "Endpoint URL (include /graphql): " url

python3 -m sgqlc.introspection \
  --exclude-deprecated \
  --exclude-description \
  -H "authorization: ${key}" \
  ${url} \
  schema.json

sgqlc-codegen schema.json schema.py
