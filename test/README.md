# Tests

Conservator CLI uses `pytest` for tests. It should have been installed if you 
followed the [Developer Installation](https://flir.github.io/conservator-cli/usage/installation.html#developers) 
instructions.

There are currently two test suites:

 - Unit tests, for checking the functionality of modules within this repo. These
   tests do not use any remote Conservator instances, and are thus fairly limited
   in scope and quantity.
 - Integration tests, for checking that CLI works with a Conservator instance.
   This requires that a local instance of Conservator is running, via docker or k8s.

Jenkins runs both. For the second, we use the latest production image.

To run tests manually, from the root directory:

```sh
$ pytest test/unit
$ pytest test/integration
```
