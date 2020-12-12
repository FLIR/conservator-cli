Installation
============

.. note::
    Conservator CLI is a private project in the FLIR organization. Make
    sure you have access, and have set up `git using SSH`_.

.. _`git using SSH`: https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/connecting-to-github-with-ssh

Basic Install
-------------

The easiest way to install Conservator CLI is with ``pip`` over ssh::

    $ pip install git+ssh://git@github.com/FLIR/conservator-cli@main

This will add the ``FLIR.conservator`` package and ``conservator`` command to
your current Python Environment.

Dependency
----------

If you're developing a project that uses Conservator CLI, you can include
the library in your ``requirements.txt`` by adding the line::

    ...
    git+ssh://git@github.com/FLIR/conservator-cli@main
    ...

You may want to specify a specific commit or tag to avoid unwanted changes.

Developers
----------

If you want to develop Conservator CLI, you'll want to start by cloning
the project::

    $ git clone git@github.com:FLIR/conservator-cli.git
    $ cd conservator-cli

Then create a virtual environment, and install the library::

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -e .

Now changes to the code will be immediately reflected in the CLI,
examples, etc.

Before committing a change, be sure to run the linter::

    $ black .

You can run tests manually::

    $ cd test
    $ pytest

You can also build the docs manually::

    $ cd docs
    $ make html

.. note::
    There is a Jenkins instance that will run tests on any new commits,
    and new documentation in the ``main`` branch will automatically be
    deployed to Github Pages.
