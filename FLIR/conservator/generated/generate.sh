#!/bin/bash


source ../../../venv/bin/activate

read -p "API Key: " key
read -p "Endpoint URL (include /graphql): " url

python3 -m sgqlc.introspection \
  --exclude-deprecated \
  --exclude-description \
  -H "authorization: ${key}" \
  ${url} \
  schema.json

sgqlc-codegen schema.json schema.py

# HACK!!!
# The built in sgqlc Date type doesn't work with Conservator.
# We need to use our own instead.
sed -i 's/sgqlc.types.datetime.Date/FLIR.conservator.generated.date.Date/g' schema.py
sed -i 's/import sgqlc.types.datetime/import FLIR.conservator.generated.date/g' schema.py

rm schema.json

# reformat generated python
black schema.py

echo "Done."
