"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.types import Collection, Dataset, Project, Video


class CollectionManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)


class VideoManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Video)


