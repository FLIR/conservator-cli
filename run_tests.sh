#!/bin/bash
DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))
nosetests -w $DIR/FLIR/conservator_cli/test/unit -v $@
$DIR/FLIR/conservator_cli/test/functional/download_collection.sh
