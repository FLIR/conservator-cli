"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.types import Project


class ProjectsManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)


