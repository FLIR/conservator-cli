# Tests

Conservator CLI uses `pytest` for tests. It should have been installed if you
followed the [Developer Installation](https://flir.github.io/conservator-cli/usage/installation.html#developers)
instructions.

There are currently two test suites:

 - Unit tests, for checking the functionality of modules within this repo. These
   tests do not use any remote Conservator instances, and are thus fairly limited
   in scope and quantity.
 - Integration tests, for checking that CLI works with a Conservator instance.
   This requires that a local instance of Conservator is running, via k8s.

## Requirements

 - In order to run the integration tests, you will need `git-lfs` installed, in order to pull the test data correctly. `git-lfs` can be installed through your package manager (e.g. `sudo apt install git-lfs`). If the files in `test/data` do not look as expected (e.g. `ls -alh` reports that they are only 100B in size, or if `file <file_name>` reports that all the files are ASCII text), running `git lfs pull` should resolve that.
 - The integration tests also require `conservator-mongo` to be a resolvable hostname. To do this, add:
 ```
 127.0.0.1        conservator-mongo
 ```
 to your `/etc/hosts` file.


**Note that running the integration tests will wipe all data from your Conservator database, apart from the `organizations`, `allowedDomains`, and `groups` collections.**

Jenkins runs both sets of tests. Jenkins runs the integration tests against a Conservator instance using the latest `prod` docker image.

To run tests manually, from the root directory:

```sh
$ pytest test/unit
$ pytest test/integration --server-deployment=<server_type>
```

where `<server_type>` is either `kind` or `minikube`, depending on how Conservator is being run. `<server_type>` defaults to `kind`.
