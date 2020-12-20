import logging
import random
import time

from FLIR.conservator.config import Config
from FLIR.conservator.connection import ConservatorConnection
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.managers import (
    CollectionManager,
    DatasetManager,
    ProjectManager,
    VideoManager,
    ImageManager,
)
from FLIR.conservator.util import base_convert

logger = logging.getLogger(__name__)


class Conservator(ConservatorConnection):
    """
    :class:`Conservator` is the highest level class of this library. It will likely be the
    starting point for all queries and operations.

    You can get an instance using the default :class:`~FLIR.conservator.config.Config`:

    >>> Conservator.default()
    <Conservator at https://flirconservator.com>

    You can create also create an instance by passing any :class:`~FLIR.conservator.config.Config`
    object:

    >>> config = Config(my_email, my_key, "https://localhost:3000")
    >>> Conservator(config)
    <Conservator at https://localhost:3000>

    :param config: The :class:`~FLIR.conservator.config.Config` object to use for this connection.
    """

    def __init__(self, config):
        super().__init__(config)
        self.collections = CollectionManager(self)
        self.datasets = DatasetManager(self)
        self.projects = ProjectManager(self)
        self.videos = VideoManager(self)
        self.images = ImageManager(self)
        logger.debug(f"Created new Conservator with config '{config}'")

    def __repr__(self):
        return f"<Conservator at {self.config.url}>"

    def get_user(self):
        """Returns the User that the provided API token authorizes"""
        return self.query(Query.user)

    ID_CHARSET = "23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz"
    ID_CHARSET_SIZE = len(ID_CHARSET)
    ID_LENGTH = 17

    @staticmethod
    def generate_id():
        """
        Generate a new ID.

        The ID consists of ``ID_LENGTH`` characters from the ``ID_CHARSET``.
        The beginning of the ID is based on the current time, and the remaining
        characters are random.
        """
        t = time.time()
        time_digits = base_convert(Conservator.ID_CHARSET_SIZE, t)[::-1]
        id_ = [Conservator.ID_CHARSET[i] for i in time_digits]
        remaining_digits = Conservator.ID_LENGTH - len(id_)
        id_ += random.sample(Conservator.ID_CHARSET, remaining_digits)
        return "".join(id_)

    @staticmethod
    def default():
        """
        Returns a :class:`Conservator` using :meth:`Config.default() <FLIR.conservator.config.Config.default>`.
        """
        return Conservator(Config.default())
