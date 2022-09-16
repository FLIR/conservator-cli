Installation
============

Basic Install
-------------

The easiest way to install Conservator CLI is with ``pip``::

    $ pip install conservator-cli

This will add the ``FLIR.conservator`` package and ``conservator`` command to
your current Python Environment.

.. note::
    if running on Linux and the ``conservator`` command is not found after
    running above install command, you may also need to ``source ~/.profile``
    on any currently open shells in order to fix your PATH
    https://github.com/FLIR/conservator-cli/issues/281

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
multiple configs. Conservator CLI stores its configurations as json files in ``~/.config/conservator-cli``.
For example, the default configuration will located at ``~/.config/conservator-cli/default.json``.
See ``conservator config --help`` for more info.


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

Installation for Windows
========================

Links
-----

https://docs.microsoft.com/en-us/windows/wsl/install
https://docs.microsoft.com/en-us/windows/wsl/troubleshooting#installation-issues
https://flir.github.io/conservator-cli/usage/installation.html

Pre install information
-----------------------

Ensure Windows is at or above required for wsl (per the first link above)
Ensure virtualization is enabled in bios
CAUTION - Right clicking in the Ubuntu shell WILL paste the contents of your clipboard

VM INSTALLATION
---------------

Press Windows key
Type powershell (or cmd)
Right click powershell (or command prompt) and choose run as administrator
In the shell type::

    $ wsl --install

Reboot when install is complete
Windows will configure some before and after reboot
After logging back in shell with ubuntu should auto start. If not, it should be under Recently added in the Windows menu
If you experience any issues, see the second link above

UBUNTU SETUP
------------

In the Ubuntu shell::

Add user name and password at prompts
Run the commands below to update, install and add the new cli commands to your path::

    $ sudo apt update
    $ sudo ln -s /usr/bin/python3 /usr/local/bin/python
    $ sudo apt install -y python3-pip
    $ pip install conservator-cli
    $ source ~/.profile

CVC SETUP
---------

Change ``staging`` below to desired target, if needed

    $ conservator config create staging

Press enter 2x (or adjust default values if desired) then enter the full url (e.g. https://staging.flirconservator.com/) and your api key
Apply default config::

    $ conservator config set-default staging

CONFIGURE GIT
-------------

Update below with your information

    $ git config --global user.email "you@example.com"
    $ git config --global user.name "Your Name"

TEST
----

Login to Conservator and use clone command from dataset -> download -> From CLI
e.g. in Ubuntu shell::

    $ cvc clone MEvzFWwcLu5Gt72C8
