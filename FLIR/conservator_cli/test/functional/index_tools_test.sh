#!/bin/bash

DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))
source $DIR/assert_statements.sh
APP=$(realpath $DIR/../../app)
ASSETS=$(realpath $DIR/../assets/conservator_dataset)
GOLD_ASSETS=$(realpath $DIR/../assets/conservator_dataset/gold)
TMP=$DIR/tmp
ONE_FAILED="False"

trap exit_handler EXIT TERM

function exit_handler() {
	if [ "$?" != 0 ]; then
		echo -e "${FAILED} $TEST_NAME"
		exit 1
	fi
	if [ "$ONE_FAILED" == "True" ]; then
		exit 1
	fi
}

function test_filter_function() {
	NAME=$1
	TEST_NAME="${NAME}.py"
	GT=$GOLD_ASSETS/${NAME}.json
	TEST=$TMP/${NAME}.json
	$APP/filter/${NAME}.py -i $ASSETS/index.json "${@:2}" -o $TEST
	assert_no_differences "$TEST_NAME" "$TEST" "$GT"
}

function test_split_function() {
	NAME=$1
	TEST_NAME="${NAME}.py"
	# GT=$GOLD_ASSETS/${NAME}.json
	TEST=$TMP/${NAME}
	mkdir -p $TEST
	$APP/split/${NAME}.py -i $ASSETS/index.json -o "$TEST" > "$TEST/out.txt"
	assert_has_string "${NAME}" "$TEST/out.txt" "3065"
}

function test_filter_function_delete() {
	NAME=$1
	TEST_NAME="${NAME}.py -d"
	GT=$GOLD_ASSETS/${NAME}_delete.json
	TEST=$TMP/${NAME}_delete.json
	$APP/filter/${NAME}.py -i $ASSETS/index.json -d "${@:2}" -o $TEST
	assert_no_differences "$TEST_NAME" "$TEST" "$GT"
}

function test_binning_function() {
	NAME=$1
	TEST_NAME="${NAME}.py"
	GT=$GOLD_ASSETS/${NAME}.txt
	TEST=$TMP/${NAME}.txt
	$APP/count/${NAME}.py -i $ASSETS/index.json "${@:2}" > $TEST
	assert_no_differences "$TEST_NAME" "$TEST" "$GT"
}

function test_inspect_function() {
	NAME=$1
	TEST_NAME="${NAME}.py"
	GT=$GOLD_ASSETS/${NAME}.txt
	TEST=$TMP/${NAME}.txt
	$APP/inspect/${NAME}.py -i $ASSETS/index.json "${@:2}" > $TEST
	assert_no_differences "$TEST_NAME" "$TEST" "$GT"
}

function test_merge_datasets() {
	NAME=$1
	TEST_NAME="${NAME}.py"
	GT=$GOLD_ASSETS/${NAME}.txt
	TEST=$TMP/${NAME}.txt
	$APP/merge_datasets.py -i $TMP/${NAME}.json -i $TMP/${NAME}_delete.json -o $TMP/${NAME}_merged.json
	#assert_no_differences "$TEST_NAME" "$TEST" "$GT"
	$APP/count/count_annotations.py -i $TMP/${NAME}_merged.json > "${TMP}/${NAME}_merged.txt"
	assert_has_string "${NAME}_merged" "$TMP/${NAME}_merged.txt" "3065"
}

if [ $TERM == xterm-256color ]; then
	COLOR_RED="\e[31m"
	COLOR_GREEN="\e[32m"
	COLOR_DEFAULT="\e[39m"
fi
PASSED=${COLOR_GREEN}PASSED:${COLOR_DEFAULT}
FAILED=${COLOR_RED}FAILED:${COLOR_DEFAULT}

echo "Setting up tmp directory..."
mkdir -p $TMP
rm -rf $TMP/*

TEST_NAME="count_annotations.py-all"
$APP/count/count_annotations.py $ASSETS/index.json -a > "$TMP/count_annotations.txt"
assert_has_string $TEST_NAME "$TMP/count_annotations.txt" "3065"

TEST_NAME="count_annotations.py-human"
$APP/count/count_annotations.py $ASSETS/index.json > "$TMP/count_annotations_human.txt"
assert_has_string $TEST_NAME "$TMP/count_annotations_human.txt" "3017"

# test_inspect_function duplicate_tracks
# test_inspect_function frames_with_overlapping_annotations -t .85 -n 1
#
# test_binning_function iou_match_count_binned_frames -t .85
# test_binning_function class_annotation_completion -l tank -l person
# test_binning_function frame_annotation_completion -l rgb,ir
# test_binning_function label_binned_annotations
# test_binning_function size_binned_frames
# test_binning_function source_type_binned_annotations
# test_binning_function track_binned_annotations
# test_binning_function track_video_binned_annotations
# test_binning_function video_binned_annotations
# test_binning_function video_binned_frames
#
# test_filter_function duplicate_track_filtered_annotations
#
# test_filter_function unused_filtered_videos
#
# test_filter_function video_filtered_frames -v "US Military and Friends hold joint Tank live fire exercise in Germany-AqRd9JR4Blo_D_resized.mkv" -v 3HZggn9BGxWyTXujZ
# test_filter_function_delete video_filtered_frames -v "US Military and Friends hold joint Tank live fire exercise in Germany-AqRd9JR4Blo_D_resized.mkv" -v 3HZggn9BGxWyTXujZ
# test_merge_datasets video_filtered_frames
#
# test_filter_function label_filtered_annotations -l tank -l person
# test_filter_function_delete label_filtered_annotations -l tank -l person
# test_merge_datasets label_filtered_annotations
#
# test_filter_function type_filtered_annotations -t human
# test_filter_function_delete type_filtered_annotations -t human
# test_merge_datasets type_filtered_annotations
#
# test_filter_function source_filtered_annotations -s EDtm4w5YTsbQQ3atQ -s x6h9pfQd9C
# test_filter_function_delete source_filtered_annotations -s EDtm4w5YTsbQQ3atQ -s x6h9pfQd9C
# test_merge_datasets source_filtered_annotations
#
# test_split_function type_split_annotations
