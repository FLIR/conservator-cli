#!/bin/bash
DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))
nosetests -w $DIR/FLIR/conservator_cli/test/unit -v $@

echo "---- STARTING FUNCTIONAL TESTS ----"

echo "---- Running download_collection.sh test ----"
$DIR/FLIR/conservator_cli/test/functional/download_collection.sh

echo "---- Running index_tools_test.sh test ----"
$DIR/FLIR/conservator_cli/test/functional/index_tools_test.sh

echo "----  ENDING FUNCTIONAL TESTS  ----"
