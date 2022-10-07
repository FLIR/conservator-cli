Installation
============

Installation on Linux
---------------------

The easiest way to install Conservator CLI is with ``pip``::

    $ pip install conservator-cli

This will add the ``FLIR.conservator`` package and ``conservator`` command to
your current Python Environment.

.. note::
    if running on Linux and the ``conservator`` command is not found after
    running above install command, you may also need to ``source ~/.profile``
    on any currently open shells in order to fix your PATH
    https://github.com/FLIR/conservator-cli/issues/281


.. _configuring_cli:

Configuring Conservator-CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you can use the command, you need to tell Conservator-CLI your API key and
other settings. Log in to your conservator instance, and find your API key. Then run::

    $ conservator config create default

Conservator CLI will ask you for your API key, the URL you use to access Conservator,
and some other settings. These settings will be saved in a config file for future use.
To verify that they're correct, run::

    $ conservator whoami

This should output information on your account. You're now free to start
with :doc:`cli_quickstart` or :doc:`cvc_guide`.

If you want to change credentials, you can edit your config by running::

    $ conservator config edit

For developers working with multiple conservator instances, you can add
multiple configs. Conservator CLI stores its configurations as json files in ``~/.config/conservator-cli``.
For example, the default configuration will located at ``~/.config/conservator-cli/default.json``.
See ``conservator config --help`` for more information.


Installation on Windows
-----------------------

Pre-installation
^^^^^^^^^^^^^^^^

 - Ensure that your Windows installation meets the mininum requirements detailed `here <https://learn.microsoft.com/en-us/windows/wsl/install>`_
 - Ensure that virtualization is enabled on your system. Consult your vendor documentation for details.

Installing Windows Subsystem for Linux (WSL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 - Open the Start menu, and type in "powershell".
 - Right-click on the PowerShell icon, and select "Run as Administrator" from the menu.
 - In the shell, type:
   ::

        $ wsl --install

   This will start the WSL installation process. Once it is complete, you will be prompted to reboot,
   which will finish the installation process.
 - After Windows has restarted, and you have logged back in, an Ubuntu command prompt should open automatically.
   If it doesn't, open the Start menu, and type in "ubuntu"; clicking the displayed icon will open the Ubuntu terminal.
 - See the `Microsoft WSL Troubleshooting Guide <https://docs.microsoft.com/en-us/windows/wsl/troubleshooting#installation-issues>`_
   for any issues with WSL installation.


Configuring Ubuntu and Installing Conservator-CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the Ubuntu shell:
 - When prompted, enter a username and password to use with Ubuntu.
 - Enter the following commands:
   ::

        $ sudo apt update
        $ sudo ln -s /usr/bin/python3 /usr/local/bin/python
        $ sudo apt install -y python3-pip
        $ pip install conservator-cli
        $ source ~/.profile

   These commands will configure Python3, and install Conservator-CLI on your system.


Configuring Git
^^^^^^^^^^^^^^^

To configure Git on WSL, use the following commands::

    $ git config --global user.email "you@example.com"
    $ git config --global user.name "Your Name"

Replace "you@example.com" with the email address you use to log in to Conservator, and "Your Name" with your name.

Once Git has been configured on your WSL system, you can follow the instructions in :ref:`configuring_cli` to configure
Conservator-CLI.

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
