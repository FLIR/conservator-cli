# Conservator CLI

Conservator CLI is a private repo. Make sure you have set up [git using SSH](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/connecting-to-github-with-ssh).

## Legacy

This branch is a fork of the `main` branch prior to some major refactoring.  It should be used
by `ConservatorTools` and other toolkits that have not been updated to the new Conservator CLI.

You can install Legacy Conservator CLI using PIP.

```
pip install -e git+ssh://git@github.com/FLIR/conservator-cli@legacy
```

You can also add Legacy Conservator CLI to your `requirements.txt`.

```
-e git+ssh://git@github.com/FLIR/conservator-cli@legacy
```

If you are starting a new toolkit or project, **please use the newer, refactored Conservator CLI**. 
Refer to the README in the `main` branch for more information.
