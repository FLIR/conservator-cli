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

**Note that running the integration tests will wipe all data from your Conservator database, apart from the `organizations`, `allowedDomains`, and `groups` collections.**

Jenkins runs both. For the second, we use the latest production image.

To run tests manually, from the root directory:

```sh
$ pytest test/unit
$ pytest test/integration --server-deployment=<server_type>
```

where `<server_type>` is either `docker`, `kind`, or `minikube`, depending on how Conservator is being run. `<server_type>` defaults to `kind`.