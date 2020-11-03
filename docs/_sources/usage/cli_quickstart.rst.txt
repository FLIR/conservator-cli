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

The first time you run this, Conservator CLI will ask you for your email and API key.
These will be saved in a config file for future use. Running again will print your
credentials. You can delete your config by running::

    $ conservator config delete

Getting Connected
-----------------

Now that we have our credentials, let's try connecting to Conservator::

    $ conservator stats

This should print out statistics for your conservator instance. If it doesn't,
you may be using a local developer installation that hasn't generated statistics
yet.

Exploring Conservator Data
--------------------------

There are several data containers on Conservator, and conservator-cli has tools
for exploring all of them.

We can query for a specific project::

    $ conservator projects get [some id]

Or get a list of all Projects::

    $ conservator projects list -p name

The same works for videos, datasets, and collections::

    $ conservator datasets list -p name
    $ conservator videos list -p name
    $ conservator collections list -p name

The ``-p`` flag controls which fields to fetch and print. You can view all
available fields using::

    $ conservator projects fields  # try with videos, datasets, and collections

We can also perform searches using Conservator's Advanced Search. To list the ids
of all datasets that contain a human annotated car, we can do::

    $ conservator datasets search "has:car"

And of course, with works with projects, videos and collections.

.. warning::

    When searching projects, conservator doesn't support Advanced Search. You
    can't include certain characters in your query (like ``:``, ``\``, and ``?``).

Downloading Data
----------------


Uploading Data
--------------


Next Steps
----------

Hopefully this guide has helped you understand the basics of Conservator CLI.

Conservator CLI does it's best to abstract away as much as possible,
but sometimes you'll want to do operations yourself. Check out the :doc:`api_quickstart`
to learn how to use the Python API to build your own tools. Using the API
is the preferred way to interface with Conservator.
