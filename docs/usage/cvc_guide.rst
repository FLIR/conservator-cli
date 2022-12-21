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

   The ``--help`` option only provides subcommands and options for the command
   it immediately follows. To get the options of a subcommand, you must explicitly
   type it. For example: ``cvc upload --help``.

Overview
--------

The basic workflow to clone and download a dataset::

    $ cvc clone DATASET_ID   # clones the dataset repo into a subdirectory
    $ cd "DATASET NAME/"     # the dataset is cloned into a directory with the same name,
                             # in the current working directory
    $ cvc download           # download media

Now, you can make modifications to ``index.json`` or ``associated_files``. In
addition to modifying existing associated files, you can add one or more new
associated files by copying them into the ``associated_files`` subdirectory.
Then, publish your changes::

    $ cvc publish "Your commit message here"

If you need to pull remote changes::

    $ cvc pull

Note that an updated ``index.json`` file may reference new frames that will have
to be downloaded (using ``cvc download``).

``index.json`` vs JSONL Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cloning a dataset using ``cvc`` will create four files that contain the dataset's metadata:

    - ``index.json`` - Contains all dataset metadata, including details on the dataset itself, details on the dataset's frames, and details on which videos were used to create the dataset.
    - ``dataset.jsonl`` - Contains dataset metadata - e.g. name, any tags applied to the dataset, dataset owner, etc.
    - ``videos.jsonl`` - Contains details of the videos used to create the dataset.
    - ``frames.jsonl`` - Contains details of the dataset's frames, including annotations and attributes

In most cases, if you wish to make changes to your dataset locally and manage those changes via ``cvc``, you can
do that by editing ``index.json``. Some datasets, howvever, are too large to manage via ``index.json``, in which
case the ``index.json`` file will only contain an error message. Such datasets can be managed and updated using JSONL files.

JSONL is very similar to plain JSON; the main difference being that while a JSON file represents a single JSON object,
a JSONL file contains multiple valid JSON objects - one per line. It is therefore very important, when updating a dataset
by editing JSONL, to ensure that you do not add any additional linebreaks.

.. note::
    - If your dataset does not have JSONL files, committing it via the Conservator UI will generate those files, and they will be available the next time you clone or pull the dataset.
    - Any changes pushed to a dataset via ``cvc`` will be reflected in both ``index.json`` and the relevant JSONL file after the dataset has been pulled.
    - If you try to commit and push changes to both ``index.json`` and one of the JSONL files at the same time, it will fail. You cannot push changes to ``index.json`` and one of the JSONL files at the same time.


Adding Frames
^^^^^^^^^^^^^

You can stage new frames to be uploaded to a dataset using the ``stage-image`` command::

    $ cvc stage-image path/to/some/file.jpg ../some/other/path.jpg etc.jpg
    $ cvc stage-image ./someimages/*.jpg

This can be reverted using the ``unstage-image`` command::

    $ cvc unstage-image path/to/some/file.jpg ../some/other/path.jpg etc.jpg

To upload the images, use the ``upload-images`` command::

    $ cvc upload-images

This will upload the images to Conservator, and add frame data to your local ``index.json`` or ``frames.jsonl`` file.
You can edit that data (to add e.g. tags, location, etc.) before committing and pushing it; or, you can upload your images,
commit the changes to ``index.json`` or ``frames.jsonl``, and push them to Conservator in a single step using the ``publish`` command::

    $ cvc publish "Uploaded new frames"

This will upload the frames to conservator, and also add them to ``frames.jsonl``. Then, it
will commit and push the changes to ``frames.jsonl``

.. note::
   Uploading will also copy staged images alongside other downloaded dataset frames
   into the ``data/`` folder. Use the ``--skip-copy`` option to not copy frames.
   Do not move images manually into the dataset folder, or the data folder.
   Also note that, after adding frames, the new frame data will be reflected in both ``frames.jsonl`` *and* ``index.json``.

Additional Reference
--------------------

For information on any command, use the ``--help`` option *after the command*. For example::

    $ cvc download --help

You can use the ``--log`` option before any command to set the log-level. For example,
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

Global Cache
^^^^^^^^^^^^

By default, Conservator-CLI uses ``.cvc/cache`` to store downloaded frames. In some
cases, it can be useful to use a single cache shared across many dataset downloads.
Duplicate frames will not be downloaded twice. To use a global cache, set the `CVC Cache Path`
to an absolute path. This can be done when initially configuring Conservator, or by editing your config::

    $ conservator config edit

Be careful, using a global config makes it difficult to clean up downloaded frames from a
single dataset.

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

Clone Timeout Workaround
^^^^^^^^^^^^^^^^^^^^^^^^

For larger datasets, you may experience timeouts when trying to clone a dataset.
While Conservator continues to optimize datasets, there is a workaround for some
use cases. Datasets downloaded in this fashion **will not have version control**
and therefore **will not support push and pull** commands. But it can be useful
for downloading frames and annotation data.

First, create a directory to hold your dataset, and enter it::

    $ mkdir my_dataset
    $ cd my_dataset

Then, download the dataset's latest ``index.json`` file::

    $ conservator datasets download-index <dataset id>

The download may take some time (and a few attempts), but should be successful
far more often than a full clone.

There are some limitations with datasets cloned with this method, as they are not
full git repositories. In general, the only command that will work without error is
``cvc download``.


Downloading Frames
^^^^^^^^^^^^^^^^^^

Download all frames from ``index.json``::

    $ cvc download

Frames will be downloaded to the ``data/`` directory within
the dataset.

You can also include analytic data::

    $ cvc download -a

This will be downloaded to ``analyticsData/``.

By default, CVC performs 10 downloads in parallel at a time. For faster connections,
you can increase this number by using the ``--pool-size`` option (``-p`` for short); for example::

    $ cvc download --pool-size 50  # download 50 frames at a time

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

You can also use relative commit references. For example, to
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

Stage images for uploading::

    $ cvc stage-image some/path/to/a.jpg

All files must be valid JPEG images. You can specify as many paths
as you want, including path wildcards. These images can be uploaded
using the ``cvc upload-images`` or ``cvc publish`` commands.

Images can be un-staged using the ``unstage-images`` command::

    $ cvc unstage-image some/path/to/a.jpg


Uploading and Adding Staged Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upload any staged images, and add them to ``frames.jsonl``::

    $ cvc upload-images

By default, the staged images will also be copied to the local dataset's ``data/``
directory. This way, you don't need to re-download the frames. To disable the copy,
use the ``--skip-copy`` option.


Validating Changes
^^^^^^^^^^^^^^^^^^

The ``index.json`` file in any dataset should match the format expected by
conservator. This format is defined by a JSON schema, and you can validate
locally::

    $ cvc validate

This command is also run (and required to pass) before adding or committing
new changes.


Making a Commit
^^^^^^^^^^^^^^^

Commit changes to ``index.json`` and ``associated_files`` with the given commit message::

    $ cvc commit "Your commit message here"

This runs ``cvc validate`` and only commits if the current ``index.json`` is valid.

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
Any modifications or additions to associated files will also be included
in the commit.


Pull Local Commits
^^^^^^^^^^^^^^^^^^

Pull the latest commits, assuming there are no local changes::

    $ cvc pull

This will update ``index.json`` and the ``associated_files`` directory.

This won't download new frames that were added to ``index.json``. You
must run ``cvc download`` again to get these new frames.
