Installation
============

Basic Install
-------------

The easiest way to install Conservator CLI is with ``pip`` over ssh::

    $ pip install git+https://github.com/FLIR/conservator-cli@main#egg=conservator-cli

This will add the ``FLIR.conservator`` package and ``conservator`` command to
your current Python Environment.

Before you can use the command, you need to tell Conservator-CLI your API key and
other settings. Log in to your conservator instance, and find your API key. Then run::

    $ conservator config create default

Conservator CLI will ask you for your API key, and some other settings.
The defaults should work for most users. These settings will be
saved in a config file for future use. To verify that they're correct, run::

    $ conservator whoami

This should output information on your account. You're now free to start
with :doc:`cli_quickstart` or :doc:`cvc_guide`.

If you want to change credentials, you can edit your config by running::

    $ conservator config edit

For developers working with multiple conservator instances, you can add
multiple configs. See ``conservator config --help`` for more info.

Dependency
----------

If you're developing a project that uses Conservator CLI, you can include
the library in your ``requirements.txt`` by adding the line::

    ...
    git+https://github.com/FLIR/conservator-cli@main#egg=conservator-cli
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

To automatically run the linter before pushing changes, you
can add the provided git hook::

    $ git config --local core.hooksPath .githooks

This will check that your changes will pass the Jenkins
linting and formatting tests.

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
