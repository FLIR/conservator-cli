# Conservator CLI

Conservator CLI is a private repo. Make sure you have set up [git using SSH](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/connecting-to-github-with-ssh).

## Installation for Users

**Note: You may want to perform a developer install (see below) to be able to 
generate and read the documentation**

You can install Conservator CLI using PIP.

```
pip install -e git+ssh://git@github.com/FLIR/conservator-cli@main
```

You can also add Conservator CLI to your `requirements.txt`.

```
-e git+ssh://git@github.com/FLIR/conservator-cli@main
```

## Installation for Developers

Use this method if you're developing Conservator CLI, or want to use the 
documentation.

#### Download

```
git clone git@github.com:FLIR/conservator-cli.git
cd conservator-cli
```

#### Install

Install the package and dependencies in a virtual environment. Make sure
you're using Python 3 to create your virtual environment.

```
python -m virtualenv venv
source venv/bin/activate
pip install .
```

#### Documentation

Documentation is generated using Sphinx.

```
cd docs
make html
```

You can view the documentation by opening `/docs/_build/html/index.html`.

Refer to the Quickstart Guide in the generated documentation for your next steps.
