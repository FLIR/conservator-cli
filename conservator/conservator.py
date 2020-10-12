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
    """
    The main interface for interacting with an instance of Conservator.

    :param config: The :class:`Config` object to use for this connection.
    """
    def __init__(self, config):
        super().__init__(config)
        self.stats = ConservatorStatsManager(self)
        self.projects = QueryableCollection(self, Project)
        self.collections = QueryableCollection(self, Collection)
        self.datasets = QueryableCollection(self, Dataset)
        self.videos = QueryableCollection(self, Video)

    def __repr__(self):
        return f"<Conservator at {self.config.url}>"
