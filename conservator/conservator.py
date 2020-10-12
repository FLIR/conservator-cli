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
from conservator.queryable_collection import QueryableCollection
from conservator.stats import ConservatorStatsManager
from conservator.type import Project, Collection, Dataset, Video


class Conservator(ConservatorConnection):
    def __init__(self, credentials, url="https://flirconservator.com/graphql"):
        """
        :param credentials: The :class:`Credentials` object to use for this connection.
        :param url: The URL of your conservator instance.
        """
        super().__init__(credentials, url)
        self.stats = ConservatorStatsManager(self)
        self.projects = QueryableCollection(self, Project)
        self.collections = QueryableCollection(self, Collection)
        self.datasets = QueryableCollection(self, Dataset)
        self.videos = QueryableCollection(self, Video)

    def __repr__(self):
        return f"<Conservator at {self.url}>"
