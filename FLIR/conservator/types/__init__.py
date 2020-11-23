"""
This modules contains types that wrap generated SGQLC types.

These wrapped types all extend :class:`TypeProxy`, and contain
a private instance of the underling SGQLC object. Initialized fields
can be accessed on the :class:`TypeProxy` instance. :class:`TypeProxy`
also provides functions to fetch new fields from Conservator.

Many of these types will also implement various Abstract
Class Types, to add functionality such as Downloading, Uploading,
Loading from Directory, etc.

Often they will include additional functions that wrap SGQLC queries.
For instance, a :class:`Collection` has :func:`Collection.get_datasets`,
which runs the GraphQL query for a collection's datasets--and returns
them as proxied :class:`Dataset` objects.
"""
from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy


class Collection(TypeProxy):
    underlying_type = schema.Collection
    by_id_query = schema.Query.collection
    search_query = schema.Query.collections


class Dataset(TypeProxy):
    underlying_type = schema.Dataset
    by_id_query = schema.Query.dataset
    search_query = schema.Query.datasets


class Project(TypeProxy):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects


class Video(TypeProxy):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos
