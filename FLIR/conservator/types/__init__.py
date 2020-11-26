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
from FLIR.conservator.types.type_proxy import TypeProxy
from .image import Image
from .video import Video
from .dataset import Dataset
from .collection import Collection
from .project import Project
