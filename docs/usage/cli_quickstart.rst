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
credentials. To verify that they're correct, run::

    $ conservator whoami

This should output information on your account.

If you want to change credentials, you can delete your config by running::

    $ conservator config delete

Basic Queries
-------------

There are four queryable types
    - Collections
    - Datasets
    - Videos
    - Projects

You can count them using `count`::

    $ conservator projects count

If you want to count the number of results in a search query, you can
include some search text (using Conservator Advanced Search syntax)::

    $ conservator projects count "ADAS"

For more advanced queries (that print the actual objects), you need to specify
which fields to include or exclude. You can use the `fields` command to list all
fields::

    $ conservator projects fields

If you don't specify fields, Conservator CLI will ask for all possible fields. This
can take a very long time to fetch for queries with more than a few results.

To list the names of all projects::

    $ conservator projects list -i name

If you want to include multiple fields, separate them with a comma::

    $ conservator projects list -i name,id

Instead of listing all objects, you can also perform searches (using Conservator Advanced
Search syntax)::

    $ conservator projects search "ADAS" -i name

These commands work with other types. For instance::

    $ conservator datasets search "ADAS" -i name

Be careful with large queries (like listing all collections), they will
take a long time.

Downloading Datasets
--------------------

The process for downloading a Dataset mirrors CVC. First, identify the ID of
the dataset you want to download. You can find this using the website, or using
a search query like ``conservator datasets search "deer" -i id``.

Now, navigate to the directory where you want to download the dataset. Note that
the dataset will be cloned in as a subdirectory, with the name of the dataset.
So if you're in ``~/Desktop``, and want to download a Dataset called ``MyFirstDataset``,
it will be cloned into ``~/Desktop/MyFirstDataset`` by default.

Then, run clone::

    $ conservator datasets clone YOUR_DATASET_ID

Cloning a dataset creates a local github repo. ``cd`` inside, and you'll find two things.
``cvc.py`` is a python script that is useful for modifying a dataset. You'll also find
``index.json``. This contains the video, image, and frame data that are a part of the
dataset. It also includes annotations, a description, and more.

Nowhere in this initial repo are any of the actual media objects. To download those, you'll
need to use the ``pull`` command::

    $ conservator datasets pull

By default, this will pull the 8-bit images into the ``data/`` directory. This parses the
``index.json`` file to find and download all of the required files.

Use ``--help`` with these commands to see more available options

Downloading Collections
-----------------------

First, find the ID of a collection you want to download using
the website, search, etc.
Then, use ``conservator collections download --help`` to view
the available options for assets to download.

For instance, to download everything recursively to the current
directory::

    $ conservator collections download ID -r -d -v -f -m

Downloading Videos
------------------

First, find the ID of a video you want to download using
the website, search, etc.

Downloads can be done using the following command::

    $ conservator videos download ID

To include video metadata, add the ``-v`` command::

    $ conservator videos download ID -v

An example for downloading a video and its metadata to the current path::

    $ conservator videos download hzYzQhpGMsTcEt6Xx -v


Interactive Mode
----------------

Conservator CLI also has a powerful and useful interactive mode::

    $ conservator interactive

This spawns a fake "shell" that emulates the directory structure of
Conservator. Type ``conservator help`` for a list of commands::

    $ help
    Usage: $ [OPTIONS] COMMAND [ARGS]...

    Commands:
      cd           Switch working directory
      collections  List child collections
      files        List file locker files
      help         Print this message
      images       List images
      info         Get information on the current collection
      ls           List collections, videos, images, and file locker files
      open         Open in browser
      pwd          Print the working directory
      tree         List child collection paths recursively
      videos       List videos

Use these commands to easily navigate around conservator,
download and upload files, edit metadata and tags, and
move media around.  Use `--help` for more information
about any specific command within the shell.
