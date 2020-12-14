"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
from FLIR.conservator.managers.media import MediaTypeManager
from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.wrappers import Collection, Dataset, Project, Video, Image


class CollectionManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)

    def from_remote_path(self, path, make_if_no_exist=False, fields=None):
        """
        Returns a collection at the specified `path`, with the specified `fields`.
        If `make_if_no_exist` is `True`, then collection(s) will be created to
        reach that path.
        """
        return self._underlying_type.from_remote_path(
            self._conservator, path, make_if_no_exist, fields
        )

    def create_root(self, name, fields=None):
        """
        Create a new root collection with the specified `name` and
        return it with the specified `fields`.
        """
        return self._underlying_type.create_root(self._conservator, name, fields)

    def create_from_parent_id(self, name, parent_id, fields=None):
        """
        Create a new child collection named `name`, under the parent collection with the
        given `parent_id`, and return it with the given `fields`.
        """
        parent = self.from_id(parent_id)
        return parent.create_child(name, fields)

    def create_from_path(self, path, fields=None):
        """
        Return a new collection at the specified `path`, with the given `fields`,
        creating new collections as necessary.  Uses :func:`from_remote_path` with
        `make_if_no_exist=True`.
        """
        return self.from_remote_path(path, make_if_no_exist=True, fields=fields)


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)

    def from_local_path(self, path="."):
        """Create a :class:`~FLIR.conservator.wrappers.Dataset` from a `path`
        containing an ``index.json`` file."""
        return self._underlying_type.from_local_path(self._conservator, path)

    def create(self, name, collections=None, fields=None):
        """
        Create a dataset with the given `name`, including the given `collections`, if specified.
        The dataset is returned with the requested `fields`.
        """
        return self._underlying_type.create(
            self._conservator, name, collections=collections, fields=fields
        )


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)

    def create(self, name, fields=None):
        """
        Create a new project with the given `name`, and return
        it with the specified `fields`.
        """
        return self._underlying_type.create(self._conservator, name, fields=fields)


class VideoManager(SearchableTypeManager, MediaTypeManager):
    def __init__(self, conservator):
        SearchableTypeManager.__init__(self, conservator, Video)
        MediaTypeManager.__init__(self, conservator)


class ImageManager(SearchableTypeManager, MediaTypeManager):
    def __init__(self, conservator):
        SearchableTypeManager.__init__(self, conservator, Image)
        MediaTypeManager.__init__(self, conservator)
