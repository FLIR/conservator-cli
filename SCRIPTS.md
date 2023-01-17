# Utility Scripts

`scripts.py` implements a number of shortcut functions to mirror the use of `yarn` in the Conservator codebase. Functions can be executed by running `scripts.py <function>`.
The following functions are available:
 - test: Runs the conservator-cli unit test suite
 - black: Runs the `black` tool to check for code that needs formatting
 - black:fix: Runs `black` and fixes any formatting issues encountered
 - all: runs `black` and `test`