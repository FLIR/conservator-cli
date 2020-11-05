CLI Quickstart
==============

This page assumes you already have Conservator CLI installed.  If you do not,
follow the :doc:`installation` instructions first.

This guide will show you how to perform basic operations using the CLI.
Please see the :doc:`api_quickstart` to get started using the Python API.

Config
------

The first step to interfacing with Conservator is setting your config.

Log in to your conservator instance, and find your API key.

Then run::

    $ conservator config

Conservator CLI will ask you for your email and API key. These will be
saved in a config file for future use. Running again will print your
credentials. If you want to change them, you can delete your config by running::

    $ conservator config delete

