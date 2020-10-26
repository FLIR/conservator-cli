Python API Quickstart
=====================

This page assumes you already have Conservator CLI installed.  If you do not,
follow the :doc:`installation` instructions first.

This guide will show you how to perform basic operations using the Python API.
Please see the :doc:`cli_quickstart` to get started using the CLI.

Config
------

A :class:`Config` object is required to connect to an instance of Conservator.
It specifies an email, API key, and URL. :class:`Config` objects can be created manually,
or loaded from a variety of sources.

The recommended way to get an instance is by using :func:`Config.default`
    >>> from conservator import Config
    >>> config = Config.default()

This will attempt to load a config from various sources, and eventually fallback to `stdin`.

See the :doc:`../api` for more details.

Getting Connected
-----------------

Once you have a :class:`Config` object, you can instantiate :class:`Conservator`
    >>> from conservator import Conservator
    >>> conservator = Conservator(config)

Equivalently, you can use :func:`Conservator.default` to create a :class:`Conservator` instance using
:func:`Config.default`.

Once you have an instance, you can check that the connection is working by querying for some statistics.
    >>> conservator.stats
    <Statistics for <Conservator at https://flirconservator.com/>>:
        id: ...

This should print out statistics for your conservator instance. If it doesn't,
you may be using a local developer installation that hasn't generated statistics
yet.

Exploring Conservator Data
--------------------------

:class:`Conservator` provides several :class:`QueryableCollection` s for searching and manipulating
:class:`QueryableType` s. These types include `projects`, `datasets`, `videos`, and `collections`.

In the following examples, you should be able to replace one type with another without trouble.

Listing
^^^^^^^

You can easily iterate through all projects:
    >>> all_projects = conservator.projects.all()
    >>> for project in all_projects:
    ...   print(project.name)

Counting
^^^^^^^^

Count all projects:
    >>> conservator.projects.count()
    96
    >>> # at the moment, this is equivalent to:
    >>> len(conservator.projects.all())
    96

Searching
^^^^^^^^^

You can use Conservator's advanced search feature to filter your queries:
    >>> adas_projects = conservator.projects.search("adas")
    >>> for project in adas_projects:
    ...   print(project.name)

Next Steps
----------

Hopefully this guide has helped you understand the basics of Conservator CLI.

Conservator CLI does it's best to abstract away as much as possible,
but sometimes that can get annoying. Check out the :doc:`advanced_guide` to learn how
the underlying features work, and how you can take advantage of them to build
your own tools.
