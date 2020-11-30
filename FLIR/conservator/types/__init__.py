"""
This modules contains types that wrap generated SGQLC types.

These wrapped types all extend :class:`~FLIR.conservator.types.type_proxy.TypeProxy`, and contain
a private instance of the underling SGQLC object. Initialized fields
can be accessed on the :class:`~FLIR.conservator.types.type_proxy.TypeProxy` instance.
:class:`~FLIR.conservator.types.type_proxy.TypeProxy` also provides functions
to fetch new fields from Conservator.

Often they will include additional functions that wrap SGQLC queries.
For instance, a :class:`~FLIR.conservator.types.collection.Collection` has
:meth:`~FLIR.conservator.types.collection.Collection.get_datasets`,
which runs the GraphQL query for a collection's datasets, and returns
them as proxied :class:`~FLIR.conservator.types.dataset.Dataset` objects.
"""
from .type_proxy import TypeProxy
from .image import Image
from .video import Video
from .dataset import Dataset
from .collection import Collection
from .project import Project