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
