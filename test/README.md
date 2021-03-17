# Tests

Conservator CLI uses `pytest` for tests. It should have been installed if you 
followed the [Installation](https://flir.github.io/conservator-cli/usage/installation.html) 
instructions.

There are currently two test suites:

 - Unit tests, for checking the functionality of modules within this repo. These
   tests do not use any remote Conservator instances, and are thus fairly limited
   in scope and quantity.
 - Integration tests, for checking that CLI works with a Conservator instance.
   This will use `Conservator.default()` for determining the connection and WILL
   leave artifacts. You should ONLY run it against a local deployment, and NOT
   against Production.
   
Jenkins runs both test suites, deploying the latest Conservator containers as 
necessary. It provides Conservator Config through environment variables.

To run tests manually, from the root directory:

```sh
$ pytest test/unit
$ pytest test/integration
```
