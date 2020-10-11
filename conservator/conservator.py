"""
Conservator is the core class in this library. You can create an instance
at flirconserator.com::

    >>> Conservator(Credentials.default())
    <Conservator at flirconservator.com>

Or specify your own url::

    >>> Conservator(Credentials.default(), url="https://localhost:3000")
    <Conservator at localhost:3000>

"""
from conservator.connection import ConservatorConnection
from conservator.generated.schema import Query, Project, Dataset, Video, Collection, Image
from conservator.queryable_collection import QueryableCollection
from conservator.queryable_type import QueryableType, ProjectQueryableType
from conservator.stats import ConservatorStatsManager


class Conservator(ConservatorConnection):
    def __init__(self, credentials, url="https://flirconservator.com/graphql"):
        """
        :param credentials: The :class:`Credentials` object to use for this connection.
        :param url: The URL of your conservator instance.
        """
        super().__init__(credentials, url)
        self.stats = ConservatorStatsManager(self)
        self.projects = QueryableCollection(self, ProjectQueryableType)
        self.datasets = QueryableCollection(self, QueryableType(Dataset,
                                                                Query.datasets,
                                                                Query.datasets_query_count,
                                                                ["frames", "shared_with", "collections", "repository", "created_at", "modified_at", "default_label_set"]))
        self.videos = QueryableCollection(self, QueryableType(Video,
                                                              Query.videos,
                                                              Query.videos_query_count,
                                                              []))
        self.collections = QueryableCollection(self, QueryableType(Collection,
                                                                   Query.collections,
                                                                   Query.collections_query_count,
                                                                   []))
        self.images = QueryableCollection(self, QueryableType(Image,
                                                              Query.images,
                                                              Query.images_query_count,
                                                              []))

    def __repr__(self):
        return f"<Conservator at {self.url}>"
