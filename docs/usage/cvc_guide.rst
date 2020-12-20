CVC Guide
=========

Conservator Version Control is a way of downloading and manipulating
datasets from Conservator. A CLI used to be distributed as a separate
``cvc.py`` file within every dataset. It is now included in Conservator CLI.

For a list of commands, open a terminal and run::

    $ conservator cvc --help

Don't worry if that command looks too long. Conservator CLI adds a shortcut
command for all things CVC::

    $ cvc --help

If you don't have the ``conservator`` or ``cvc`` command, please install
the Conservator CLI library by following the :doc:`installation` guide.

.. note::
   The following operations are supported via CVC:

    - Add frames (JPEG files only)
    - Delete frames
    - Add annotations
    - Add/edit custom dataset/frame metadata

.. note::
   Adding associated files is technically a feature, but you'll have to
   manually use ``git`` to add/commit files within the ``associated_files`` directory.

   TODO: Add support for this through ``cvc``

Overview
--------

The basic workflow to clone and download a dataset::

    $ cvc clone DATASET_ID   # clone's the dataset repo into a subdirectory
    $ cd "DATASET NAME/"     # the default directory is the name of the dataset
    $ cvc download           # download media

Now, you can make modifications to ``index.json``. Then, publish your changes::

    $ cvc publish "Your commit message here"

If you need to pull remote changes to ``index.json``::

    $ cvc pull

Note that this may reference new frames that will have to be downloaded (using ``cvc download``).

Adding Frames
^^^^^^^^^^^^^

You can stage new frames to be uploaded to a dataset using the ``add`` command::

    $ cvc add path/to/some/file.jpg ../some/other/path.jpg etc.jpg
    $ cvc add ./someimages/*.jpg

Then, upload and publish your new frames::

    $ cvc publish "Uploaded new frames or whatever"

This will upload the frames to conservator, and also add them to ``index.json``. Then, it
will commit and push the changes to ``index.json``

.. note::
   Uploading will also copy staged images alongside other downloaded dataset frames,
   if it is detected that media has been downloaded (by the presence of a ``data/``
   directory).

Additional Reference
----------------------------

You can use the ``--log`` option before any command to set the log-level. For instance,
to see debug prints while uploading some frames::

    $ cvc --log DEBUG upload

By default, CVC operates in the current working directory. However, you can add ``-p`` or
``--path`` to work in a different directory::

    $ cvc --path "/home/datasets/some other dataset" pull

A local dataset directory must contain an ``index.json`` file to be considered valid.

Datasets are downloaded as `git` repositories. Many ``cvc`` commands simply wrap ``git``
commands. Unfortunately, not many features of ``git`` are supported by Conservator (such
as branching). For that reason, please avoid using raw ``git`` commands, and prefer using
``cvc`` for everything. There are also plans to transition away from ``git``, so getting
used to using ``cvc`` now will make that transition easier later.

Cloning
^^^^^^^
Clone a dataset by id
``cvc clone``

Downloading Frames
^^^^^^^^^^^^^^^^^^
Download media files from index.json
``cvc download``

Commit History
^^^^^^^^^^^^^^
Show log of commits
``cvc log``

Checking out a Commit
^^^^^^^^^^^^^^^^^^^^^
Checkout a commit hash
``cvc checkout``

Commit Info
^^^^^^^^^^^
Shows information on a specific commit or object
``cvc show``

Status
^^^^^^
Print staged images and files
``cvc status``

Current Changes
^^^^^^^^^^^^^^^
Show changes in index.json since last commit
``cvc diff``

Staging New Images
^^^^^^^^^^^^^^^^^^
Stage images for uploading and adding to index.json
``cvc add``

Uploading and Adding Staged Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Upload staged images and add them to index.json
``cvc upload``

Making a Commit
^^^^^^^^^^^^^^^
Commit changes to index.json with the given message
``cvc commit``

Push Local Commits
^^^^^^^^^^^^^^^^^^
``cvc push``

Publish: Upload, Commit, Push
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Upload staged images (if any), then commit with message and push
``cvc publish``

Pull Local Commits
^^^^^^^^^^^^^^^^^^
Pull the latest commits
``cvc pull``

