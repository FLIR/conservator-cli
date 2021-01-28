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

Conservator CLI will ask you for your API key, and some other settings.
The defaults should work for most users. These settings will be
saved in a config file for future use. To verify that they're correct, run::

    $ conservator whoami

This should output information on your account.

If you want to change credentials, you can delete your config by running::

    $ conservator config --delete

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

The process for downloading a Dataset mirrors CVC.  To see the available commands::

    $ conservator cvc --help

A shortcut to this command also exists::

    $ cvc --help

You can clone a dataset into the current directory using its ID::

    $ cvc clone DATASET_ID

Once cloned, you can download media with ``cvc download`` from within the dataset
directory.

Please see the :doc:`cvc_guide` for more details.

Downloading Collections
-----------------------

First, find the ID of a collection you want to download using
the website, search, etc.
Then, use ``conservator collections download --help`` to view
the available options for assets to download.

For instance, to download everything recursively to the current
directory::

    $ conservator collections download ID -r -d -v -f -m

Downloading Media
------------------

First, find the ID of a video or image you want to download using
the website, search, etc.

Downloads can be done using the following command::

    $ conservator videos download ID

To include metadata, add the ``-m`` command::

    $ conservator videos download ID -m

If you only want metadata, use ``-mo``.

An example for downloading a video and its metadata to the current path::

    $ conservator videos download hzYzQhpGMsTcEt6Xx -v

The same commands also work for images (just replace ``videos`` with
``images``).

Uploading Media
---------------

Media can be uploaded using the ``conservator collections upload`` command. This
command takes a remote collection, and a local path. Its the preferred method of
uploading media, as it has safeguards to retry failures, perform uploads in parallel,
and output status clearly. To recursively create remote collections and uploads media
from a local path::

    $ conservator collections upload --recursive /remote/collection/path /local/path/to/upload

This command has options to filter the uploaded files and behavior. For all options,
run::

    $ conservator collections upload --help

.. note::
    Currently, this command only accepts a directory path and can't upload a single file
    path. You would need to create a directory containing only the single file, or use
    an individual media upload command as explained below.

Alternatively, individual Images and videos can be uploaded with the `upload` command::

    $ conservator videos upload path/to/local/media.mp4 /path/on/conservator/

By default, the media will be uploaded with the same name as the local file.
If you want to use a different name, you can specific it using ``--remote-name``
(``-r`` for short)::

    $ conservator videos upload path/to/local/media.mp4 /path/on/conservator/ -r my_name.mp4

By default, the path on conservator must exist, but it can also be useful to
upload to a path that doesn't exist. You can create any required collections
using ``--create-collections`` (``-c`` for short)::

    $ conservator videos upload path/to/local/media.mp4 /path/to/create -c

Again, you can use these commands for uploading both videos or images.

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
