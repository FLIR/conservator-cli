#!/bin/bash
DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))
source $DIR/assert_statements.sh
APP=$(realpath $DIR/../../app)
TMP=$DIR/tmp/download_collection
FAILURE=0

trap exit_handler EXIT TERM

mkdir -p $TMP
rm -rf $TMP/*

cd $TMP
$APP/download/download_collection.py /integration-test -u $CONSERVATOR_EMAIL -t $CONSERVATOR_TOKEN > $TMP/download_collection.log
assert_file_exists downloaded_collection $TMP/integration-test
touch $TMP/integration-test/delete_me.txt
$APP/download/download_collection.py /integration-test -u $CONSERVATOR_EMAIL -t $CONSERVATOR_TOKEN -o -a -d -m > $TMP/download_collection_all.log

assert_file_exists downloaded_subfolder $TMP/integration-test/subfolder
assert_file_exists downloaded_video_metadata $TMP/integration-test/5_second_cut.json
assert_file_exists downloaded_associated_files_png $TMP/integration-test/car_arrow.png
assert_file_exists downloaded_associated_files_json $TMP/integration-test/nntc_config.json
assert_file_exists downloaded_dataset_git $TMP/integration-test/test/index.json
assert_file_exists downloaded_dataset_cvc integration-test/test/data/video-n22QqCcd2vRWZGK3z-frame-000225-AKP56dB2LuL5HY7hq.jpg
assert_file_does_not_exist overwrite_file integration-test/delete_me.txt
