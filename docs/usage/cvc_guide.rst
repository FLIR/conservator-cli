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
    - Adding, removing, or changing associated files

Overview
--------

The basic workflow to clone and download a dataset::

    $ cvc clone DATASET_ID   # clone's the dataset repo into a subdirectory
    $ cd "DATASET NAME/"     # the default directory is the name of the dataset
    $ cvc download           # download media

Now, you can make modifications to ``index.json`` or ``associated_files``. Then,
publish your changes::

    $ cvc publish "Your commit message here"

If you need to pull remote changes::

    $ cvc pull

Note that an updated ``index.json`` file may reference new frames that will have
to be downloaded (using ``cvc download``).

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

Datasets are downloaded as ``git`` repositories. Many ``cvc`` commands simply wrap ``git``
commands. Unfortunately, not many features of ``git`` are supported by Conservator (such
as branching). For that reason, please avoid using raw ``git`` commands, and prefer using
``cvc`` for everything. There are also plans to transition away from ``git``, so getting
used to using ``cvc`` now will make that transition easier later.

Cloning
^^^^^^^

Clone a Dataset from a known ID::

    $ cvc clone DATASET_ID

By default, this will clone the dataset into subdirectory of the current directory,
with the name of the dataset. To clone somewhere else, use the ``--path`` option::

    $ cvc clone DATASET_ID --path where/to/clone/

This directory should be empty.

If you want to checkout a specific commit after cloning, you can include
the ``--checkout`` option::

    $ cvc clone DATASET_ID --checkout COMMIT_HASH

You can then use ``cvc checkout HEAD`` to return to the most recent commit.


Downloading Frames
^^^^^^^^^^^^^^^^^^

Download all frames from ``index.json``::

    $ cvc download

Frames will be downloaded to the ``data/`` directory within
the dataset.

You can also include analytic data::

    $ cvc download -a

This will be downloaded to ``analyticsData/``.


Commit History
^^^^^^^^^^^^^^

Show log of commits::

    $ cvc log

You can use ``cvc checkout`` to view files at a specific commit, or
``cvc show`` to see more info about a specific commit.


Checking out a Commit
^^^^^^^^^^^^^^^^^^^^^

Checkout a commit hash::

    $ cvc checkout COMMIT_HASH

You can also use relative commit references. For instance, to
reset to the most recent commit (such as when you want to return after
checking out some other commit)::

    $ cvc checkout "HEAD"

.. warning::
   Checking out a commit is a destructive action. Any local changes will be
   overwritten.


Commit Info
^^^^^^^^^^^

Shows information on the most recent commit::

    $ cvc show

You can also view a specific commit by passing its hash::

    $ cvc show COMMIT_HASH


Status
^^^^^^

Print staged images and changed files::

    $ cvc status

Use ``cvc publish`` to send these changes to Conservator.

Current Changes
^^^^^^^^^^^^^^^

Show changes in ``index.json`` and ``associated_files`` since last commit::

    $ cvc diff

Staging New Images
^^^^^^^^^^^^^^^^^^

Stage images for uploading and adding to ``index.json``::

    $ cvc add some/path/to/a.jpg

All files must be valid JPEG images. You can specify as many paths
as you want, including path wildcards. These images can be uploaded
using the ``cvc upload`` or ``cvc publish`` commands.


Uploading and Adding Staged Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upload any staged images, and add them to ``index.json``::

    $ cvc upload

If it's detected that you've downloaded frames before (by the presence of a ``data/``
directory), then the images will also be copied there. This way you
don't need to re-download the frames.


Making a Commit
^^^^^^^^^^^^^^^

Commit changes to ``index.json`` and ``associated_files`` with the given commit message::

    $ cvc commit "Your commit message here"


Push Local Commits
^^^^^^^^^^^^^^^^^^

Push your local commits to Conservator::

    $ cvc push


Publish: Upload, Commit, Push
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A frequent usage pattern is to upload frames, commit changes to ``index.json``,
and push. All three steps can be done with a single command::

    $ cvc publish "Your commit message"

If you don't have any images staged, the upload process will be skipped.
So this is also a suitable replacement for commit, push.

At this time, associated files will not be included in this commit.


Pull Local Commits
^^^^^^^^^^^^^^^^^^

Pull the latest commits, assuming there are no local changes::

    $ cvc pull

This will update ``index.json`` and the ``associated_files`` directory.

This won't download new frames that were added to ``index.json``. You
must run ``cvc download`` again to get these new frames.
