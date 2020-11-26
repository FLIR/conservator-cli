"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.types import Collection, Dataset, Project, Video, Image


class CollectionManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)

    def from_local_path(self, path="."):
        """Create a :class:`~FLIR.conservator.types.Dataset` from a `path`
        containing an ``index.json`` file."""
        return self._underlying_type.from_local_path(self._conservator, path)


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)


class VideoManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Video)


class ImagesManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Image)


