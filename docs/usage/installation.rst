Installation
============

Basic Install
-------------

The easiest way to install Conservator CLI is with ``pip``::

    $ pip install conservator-cli

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


Developers
----------

If you want to develop Conservator CLI, you'll want to start by cloning
the project::

    $ git clone git@github.com:FLIR/conservator-cli.git
    $ cd conservator-cli

To manage test data, CLI uses ``git-lfs``. Install the custom hooks, and
pull test data::

    $ git config --local core.hooksPath .githooks
    $ git pull

Then create a virtual environment, and install the library::

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -e .

Changes to the code will be immediately reflected in the CLI,
examples, etc.

There a few additional tools used by developers, such as `pytest`, `black`,
etc. To install them, use `requirements.txt`::

    $ pip install -r requirements.txt

Before committing a change, be sure to run the linter::

    $ black .

If you installed the git hooks as above (not using ``git lfs install``), the
linter will automatically run before you attempt to push any changes.

You can run tests manually::

    $ cd test
    $ pytest test/unit
    $ pytest test/integration

.. note::
    Integration tests require a local running instance of FLIR Conservator.
    For more info, see the ``README`` in the test directory.

You can also build the docs manually::

    $ cd docs
    $ make html

.. note::
    There is a Jenkins instance that will run tests on any new commits,
    and new documentation in the ``main`` branch will automatically be
    deployed to Github Pages.
