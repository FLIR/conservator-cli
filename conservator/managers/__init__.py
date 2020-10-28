from conservator.types import Project, Dataset, Video, Collection
from conservator.connection import ConservatorMalformedQueryException
from conservator.managers.searchable import SearchableTypeManager
from conservator.managers.downloadable import DownloadableTypeManager


class ProjectsManager(SearchableTypeManager, DownloadableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)

    def search(self, search_text, **kwargs):
        # TODO: find out what other characters break projects queries
        bad_chars = ":?\\"
        for char in bad_chars:
            if char in search_text:
                raise ConservatorMalformedQueryException(f"You can't include '{char}' in a projects search string")
        return super().search(search_text, **kwargs)


class DatasetsManager(SearchableTypeManager, DownloadableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)


class VideosManager(SearchableTypeManager, DownloadableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Video)


class CollectionsManager(SearchableTypeManager, DownloadableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)

