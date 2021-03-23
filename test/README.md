# Tests

Conservator CLI uses `pytest` for tests. It should have been installed if you 
followed the [Installation](https://flir.github.io/conservator-cli/usage/installation.html) 
instructions.

There are currently two test suites:

 - Unit tests, for checking the functionality of modules within this repo. These
   tests do not use any remote Conservator instances, and are thus fairly limited
   in scope and quantity.
 - Integration tests, for checking that CLI works with a Conservator instance.
   This assumes a local, standard, docker installation of Conservator is running.
   Tests will fail if this isn't the case.

Jenkins only runs the first. Soon it will also run the second against the latest 
conservator image.

To run tests manually, from the root directory:

```sh
$ pytest test/unit
$ pytest test/integration
```
