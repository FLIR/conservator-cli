#!/bin/bash

# Get full directory path to current script
SCRIPT_PATH="$(dirname "${BASH_SOURCE[0]}")"
SCRIPT_PATH="$(realpath "${SCRIPT_PATH}")"
BASE_PATH="$(realpath "${SCRIPT_PATH}/../../..")"

read -p "API Key: " key
read -p "Endpoint URL (include /graphql): " url

python3 -m sgqlc.introspection \
  --exclude-description \
  -H "authorization: ${key}" \
  ${url} \
  ${SCRIPT_PATH}/schema.json

sgqlc-codegen schema ${SCRIPT_PATH}/schema.json ${SCRIPT_PATH}/schema.py

# HACK!!!
# The built in sgqlc Date type doesn't work with Conservator.
# We need to use our own instead.

#For it to run on Macos
if [[ "$OSTYPE" == "darwin"* ]]; then
  gsed -i 's/sgqlc.types.datetime.Date/FLIR.conservator.generated.date.Date/g' ${SCRIPT_PATH}/schema.py
  gsed -i 's/import sgqlc.types.datetime/import FLIR.conservator.generated.date/g' ${SCRIPT_PATH}/schema.py
else
  sed -i 's/sgqlc.types.datetime.Date/FLIR.conservator.generated.date.Date/g' ${SCRIPT_PATH}/schema.py
  sed -i 's/import sgqlc.types.datetime/import FLIR.conservator.generated.date/g' ${SCRIPT_PATH}/schema.py
fi

md5sum ${SCRIPT_PATH}/schema.json | cut -d ' ' -f 1 | tee "$BASE_PATH/api_version.txt"
rm ${SCRIPT_PATH}/schema.json

# reformat generated python
black ${SCRIPT_PATH}/schema.py

echo "Done."
