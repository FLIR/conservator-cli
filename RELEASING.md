# Releasing a new version

## Schema Updates

Note that, if the Conservator GraphQL API changes, the Conservator CLI schema should be updated. This can be done by running `FLIR/conservator/generated/generate.sh`. This will regenerate the `FLIR/conservator/generated/schema.py` file to match the deployed schema.

## Tagging Release

First checkout main and pull the latest commits. All releases
should be on `main` branch.

```bash
git checkout main
```

Then, tag the commit with the release version. The `version` must
follow [PEP 440](https://www.python.org/dev/peps/pep-0440/). For instance: `1.1.1`, `1.2.34`.

```bash
git tag -a [version] -m "Release [version]"
```

Then, push the tag:

```bash
git push origin [version]
```

The latest tagged version of Conservator-CLI should be considered as the latest release; Conservator-CLI on PyPi will no longer be maintained.
