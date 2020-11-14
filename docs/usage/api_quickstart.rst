Python API Quickstart
=====================

This page assumes you already have Conservator CLI installed.  If you do not,
follow the :doc:`installation` instructions first.

This guide will show you how to perform basic operations using the Python API.
Please see the :doc:`cli_quickstart` to get started using the CLI.

If you're looking for more detailed information on how Conservator CLI is structured,
view the :doc:`api_advanced` and :doc:`../api`.

Config and Getting Connected
----------------------------

Typically, you won't have to manually worry about loading different :class:`~FLIR.conservator.config.Config`
objects, and can just use the default for connections.

Conservator CLI makes getting connected with the default configuration
pretty easy::
    >>> from FLIR.conservator.conservator import Conservator
    >>> conservator = Conservator.default()
    >>> print(conservator)
    <Conservator at https://flirconservator.com/>

If someone doesn't have a config already, this will prompt them for their info,
and save it in a file for the future. Now that you have an instance of :class:`~FLIR.conservator.conservator.Conservator`,
you are free to start running queries.

Basic Queries
-------------

Let's start with something simple.  Listing the names of all the projects
on conservator::
    >>> all_projects = conservator.projects.all()
    >>> all_projects.include_field("name")
    >>> for project in all_projects:
    ...     print(project.name)

Running this will demonstrate a few things. First off, using :meth:`~FLIR.conservator.managers.searchable.SearchableTypeManager.all`
doesn't immediately execute the query. It returns a :class:`~FLIR.conservator.paginated_query.PaginatedQuery`,
which lets you specify which fields you want to include in the results. By
default, it will request all fields of its type (in this case, :class:`~FLIR.conservator.types.Project`).
Since we only want to see the `name`, we call :meth:`~FLIR.conservator.paginated_query.PaginatedQuery.include_field`
with it specified.

Once we've set up the fields we want to return from our query, we need to
actually send it to Conservator and iterate through the results. This is
done automatically when you attempt to iterate through a :class:`~FLIR.conservator.paginated_query.PaginatedQuery`
using `for ... in` (or anything else that calls `__iter__`).

The :class:`~FLIR.conservator.types.Project` instances returned from the iteration
will contain the fields we included.

Querying for all Fields
^^^^^^^^^^^^^^^^^^^^^^^

Let's say we were interested in all of the fields in :class:`~FLIR.conservator.types.Project`.
We can repeat above, without including :meth:`~FLIR.conservator.paginated_query.PaginatedQuery.include_field`.
    >>> all_projects = conservator.projects.all()
    >>> for project in all_projects:
    ...     print(project)

This will print a few errors, then the projects (which will be a lot of text).

The errors are expected, because we're requesting every possible field. A few fields
may have been deprecated, or be undefined in the Conservator database. When we tried
running the query, the server returned an error. Luckily, Conservator CLI was able to
catch it, and find the `problematic field`. It tried the request again, excluding that
field.

Once the request went through, your results were returned. Conservator has a :class:`~FLIR.conservator.fields_manager.FieldsManager`
to keep track of the `problematic fields` in past requests, and to exclude them
in future ones.

Specifying Fields
^^^^^^^^^^^^^^^^^

The ability to specify fields is a powerful feature of GraphQL, the API framework
used by FLIR Conservator. In many API requests in Conservator CLI, you will have to
specify which fields you are interested in. Usually, these are provided using
a :class:`~FLIR.conservator.fields_request.FieldsRequest`. These let you `include`
or `exclude` fields in your request.

A :class:`~FLIR.conservator.paginated_query.PaginatedQuery` has an internal
:class:`~FLIR.conservator.fields_request.FieldsRequest` that it maintains and uses
when executing the actual query.

See the documentation on :class:`~FLIR.conservator.fields_request.FieldsRequest`
for more information on including and excluding fields, subfields, etc.

Other types of Queries
----------------------

You can do more than just list all Projects on conservator.

Conservator also provides utilities for querying Collections,
Datasets and Videos.

Each query endpoint can list all of its type (as used above), or
perform searches using FLIR Conservator's Advanced Search feature.

For example, if we wanted to print the names of all datasets that
contains the word `ADAS`, we could do the following::
    >>> adas_datasets = conservator.projects.search("ADAS")
    >>> adas_datasets.include_field("name")
    >>> for ds in adas_datasets:
    ...     print(ds.name)

Sometimes you'll only want (or expect) a single result. You
can short-circuit the full query using :meth:`~FLIR.conservator.paginated_query.PaginatedQuery.first`::
    >>> adas_datasets = conservator.projects.search("ADAS")
    >>> adas_datasets.include_field("name")
    >>> dataset = adas_datasets.first()
    >>> print(dataset.name)

Another frequent use is counting the number of results. This can be done
with :meth:`~FLIR.conservator.managers.searchable.SearchableTypeManager.count_all`
for all instances, or :meth:`~FLIR.conservator.managers.searchable.SearchableTypeManager.count`
for a specific `search text`::
    >>> adas_projects_count = conservator.projects.count("ADAS")
    >>> print(adas_projects_count)

Populating Fields Later
-----------------------

Sometimes you'll need to add fields to an object after your initial request.
For instance, assume you queried for a Project's `id`::
    >>> adas_datasets = conservator.projects.search("ADAS")
    >>> adas_datasets.include_field("id")
    >>> dataset = adas_datasets.first()
    >>> print(dataset.id)

But later want to print its name.  You can fetch the `name` field using
:meth:`~FLIR.conservator.types.type_proxy.TypeProxy.populate`::
    >>> from FLIR.conservator.fields_request import FieldsRequest
    >>> fields = FieldsRequest()
    >>> fields.include_field("name")
    >>> dataset.populate(fields)
    >>> print(dataset.name)

If for some reason you have an ID, but don't have an instance of the correct
type to use :meth:`~FLIR.conservator.types.type_proxy.TypeProxy.populate`, you
can create one with :meth:`~FLIR.conservator.managers.type_manager.TypeManager.from_id`,
and then populate the fields::
    >>> collection = conservator.collections.from_id("some_collection_id")
    >>> fields = FieldsRequest()
    >>> fields.include_field("path")
    >>> collection.populate(fields)
    >>> print(collection.path)

You can also call :meth:`~FLIR.conservator.types.type_proxy.TypeProxy.populate` with
no argument to populate all fields::
    >>> collection = conservator.collections.from_id("some_collection_id")
    >>> collection.populate()
    >>> print(collection.path)

Next Steps
----------

Take a look at the :doc:`api_advanced` and :doc:`../api` for more
info on the structure of Conservator CLI.

You may also want to check out the `examples` directory.
