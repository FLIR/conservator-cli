if [ $TERM == xterm-256color ]; then
	COLOR_RED="\e[31m"
	COLOR_GREEN="\e[32m"
	COLOR_DEFAULT="\e[39m"
fi
PASSED=${COLOR_GREEN}PASSED:${COLOR_DEFAULT}
FAILED=${COLOR_RED}FAILED:${COLOR_DEFAULT}

function exit_handler() {
  if [ "$?" != 0 ]; then
    echo -e "${FAILED} $TEST_NAME"
    FAILURE=1
  fi
  if [ $FAILURE = 1 ]; then
    exit 2
  fi
}

function assert_file_exists() {
  local TEST_NAME=$1
  local FILE_PATH=$2
  if [ -e $FILE_PATH ] ; then
    echo -e "${PASSED} $TEST_NAME"
  else
    echo -e "${FAILED} $TEST_NAME"
    FAILURE=1
  fi
}

function assert_file_does_not_exist() {
  local TEST_NAME=$1
  local FILE_PATH=$2
  if [ ! -e $FILE_PATH ] ; then
    echo -e "${PASSED} $TEST_NAME"
  else
    echo -e "${FAILED} $TEST_NAME"
    FAILURE=1
  fi
}

function assert_has_string() {
  local TEST_NAME=$1
  local FILE=$2
  local GREP_STRING=$3
  if cat "$FILE" | grep -q "$GREP_STRING"; then
    echo -e "${PASSED} $TEST_NAME"
  else
    echo -e "${FAILED} $TEST_NAME"
    FAULURE=1
  fi
}

function assert_no_differences() {
  local TEST_NAME=$1
  local TEST=$2
  local GT=$3
  DIFF=$(diff $TEST $GT)
  if [ "$?" == 2 ]; then
    echo -e "${FAILED} $TEST_NAME"
    FAILURE="1"
  if [ $EXIT_EARLY ]; then exit; fi
    return
  fi
  if [ ! "$DIFF" == "" ] ; then
    echo "Changes Detected in diff:"
    echo "diff $TEST $GT"
    echo -e "${FAILED} $TEST_NAME"
    FAILURE=1
    if [ $EXIT_EARLY ]; then exit; fi
  else
    echo -e "${PASSED} $TEST_NAME"
  fi
}
