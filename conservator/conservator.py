"""
:class:`Conservator` is the highest level class of this library. It should be the
starting point for all queries and operations.

To get an instance using the default :class:`Config`::

    >>> Conservator.default()
    <Conservator at https://flirconservator.com>


You can create also create an instance by passing any :class:`Config`
object.

    >>> config = Config(my_email, my_key, "https://localhost:3000")
    >>> Conservator(config)
    <Conservator at https://localhost:3000>

"""
from conservator.config import Config
from conservator.connection import ConservatorConnection
from conservator.queryable_collection import QueryableCollection
from conservator.stats import ConservatorStatsManager
from conservator.type import Project, Collection, Dataset, Video


class Conservator(ConservatorConnection):
    """
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

    @staticmethod
    def default():
        """
        Returns a :class:`Conservator` using :func:`Config.default`.
        """
        return Conservator(Config.default())
