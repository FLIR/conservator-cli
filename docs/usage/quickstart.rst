Quickstart
==========

This page assumes you already have Conservator CLI installed.  If you do not,
follow the :doc:`installation` instructions first.

Credentials
-----------

The first step to interfacing with Conservator is setting your credentials.

Log in to your conservator instance, and find your API key.

Then open up a Python shell, and run::

    >>> from conservator import *
    >>> credentials = Credentials.default()

The first time you run this, Conservator CLI will ask you for your email and API key.
These will be saved in a config file for future use. There are a variety of ways to
provide credentials, but :func:`Credentials.default` is generally the
most reliable. See :class:`Credentials` for more information.

Getting Connected
-----------------

Now that we have our credentials, let's try connecting to Conservator::

    >>> conservator = Conservator().using_credentials(credentials)
    >>> conservator.stats
    Statistics for <Conservator at flirconservator.com>:
      Projects: 43
      Users: 123
      Datasets: 312
      Videos: 894
      Frames: 398273
      Annotations: 2039171

That was easy! Note that by default, Conservator CLI uses `flirconservator.com`_.
You can change this by specifying the ``url`` to :class:`Conservator`::

    >>> a = Conservator(url="https://myconservatorinstance.com")
    >>> b = Conservator(url="https://localhost:3000/")

.. _`flirconservator.com`: https://flirconservator.com

Exploring Conservator Data
--------------------------

Data on conservator is organized into Projects, which consist of Datasets.

We can query for a project::

    >>> conservator.projects.first()
    <Project name="280 HD">

Or a list of all Projects::

    >>> list(conservator.projects.all())
    [<Project name="280 HD">, <Project name="280HD-release">, ...]

It's important to note that queries like ``all`` are time consuming.  Instead
of gathering everything at once, Conservator CLI returns a generator, that
performs a series of paged queries to serve the entities as they are needed.
You can read more about this process by looking at :class:`conservator.QueryableCollection`.

You can also perform more advanced queries by leveraging Conservator's :doc:`advanced_search`
feature::

    >>> image = conservator.images.search("before:2017-01-09 AND location:Goleta").first()
    >>> image
    <Image name="20191031_182208_168_8b.JPG">


Annotations
-----------

You can use :func:`Image.annotations` to automatically fetch the image's annotations::

    >>> list(image.annotations)
    [<Annotation label="car">, <Annotation label="person">]

You can also filter annotations::

    >>> list(image.annotations.with_props(label="car"))
    [<Annotation label="car">]


Downloading Images
----------------

When we get an :class:`Image` instance, we haven't actually gotten any of
the image's data. We've only gotten a bit of meta data::

    >>> image.details
    Details for <Image name="20191031_182208_168_8b.JPG">
        name="20191031_182208_168_8b.JPG"
        uploaded_by="someone@flir.com"
        id="Jrvb4bJq4Dicn7cZQ"

    Run .populate to load more details.

We can grab more meta data by running :func:`Image.populate()`. This will
add details such as the image's size, hash, and tags.  If you attempt to read
any of those fields before calling :func:`Image.populate()`, it will be called
for you.

Although we've gotten the image's meta data, we still don't have the actual image.
If we want to save it to the disk, we can use :func:`Image.download_to`.

    >>> image.download_to("~/Desktop")

Alternatively, we can get the image data as a ``numpy`` array::

    >>> image.download_as_numpy()
    ... 512x512 numpy array

In either case, we can specify if we want to use the full 16 bit images:

    >>> image.download_to("~/Desktop/16-bit.jpg", full_bits=True)


Uploading Data
--------------

It's very easy to add modifications to existing data::

    >>> annotation = list(image.annotations)[0]
    >>> annotation.label = "truck"
    >>> image.has_changed_locally
    True
    >>> image.upload()

To create new information, you need to get an instance of the class you want to upload::

    >>> dataset = conservator.make_new_dataset(name="New Dataset")
    >>> dataset.created_locally
    True
    >>> dataset.upload()

In either case, Conservator CLI is smart enough to know if it needs to submit an update query,
or an entirely new object.

In the case of images, you can pass a path::

    >>> new_image = conservator.make_new_image(name="New Image", path="~/Desktop/test.jpg")
    >>> new_image.created_locally
    True
    >>> new_image.upload()


Mass Operations and Statistics
------------------------------

Sometimes you're going to want to do big, complicated things.
For instance, lets say you want to determine how many images in all
of conservator contain a car::

    >>> conservator.images.search("has:car").count()
    34221

This operation probably took a while to complete, and it would take even
longer to compile a dictionary of all possible counts for every classifier.

If you want to perform lots of operations, it can be helpful to download
a lot of data locally, all at once. To do this, we use the :class:`ConservatorCache`::

    >>> conservator.cache
    <DataCache for <Conservator at flirconservator.com>>
    >>> conservator.cache.download_image_data()
    Starting <MassOperation op="download" type="image">...
    .
    .
    ...


See the :doc:`mass_operations` guide for more info.

Next Steps
----------

Hopefully this guide has helped you understand the basics of Conservator CLI.

Conservator CLI does it's best to abstract away as much as possible,
but sometimes that can get annoying. Check out the :doc:`advanced_guide` to learn how
the underlying features work, and how you can take advantage of them to build
your own tools.
