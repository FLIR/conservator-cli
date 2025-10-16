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

## Deploying Release

Open Conservator CLI (FLIR-Ubuntu-Native-Build -> conservator-cli) in FLIR Jenkins, go click the new version under the Tags tab.
On the side, click `Build Now`. This runs all tests, and if they pass, releases to PyPI.

Nathan Wachholz and Andres Prieto-Moreno currently have access to the PyPI account.

## Check Release

Verify the new version is released on the [PyPI page](https://pypi.org/project/conservator-cli/), and try `pip install conservator-cli` from a new venv.
