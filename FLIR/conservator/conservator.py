import logging
import random
import re
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
    def is_valid_id(id_):
        return re.fullmatch(
            r"^[23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz]{17}$", id_
        )

    @staticmethod
    def default(save=True):
        """
        Returns a :class:`Conservator` using :meth:`Config.default() <FLIR.conservator.config.Config.default>`.
        """
        return Conservator(Config.default(save=save))

    def get_media_instance_from_id(self, media_id, fields=None):
        """
        Returns a Video or Image object from an ID. These types are checked in
        this order, until :meth:`~FLIR.conservator.managers.type_manager.id_exists`
        returns `True`. If neither matches, an :class:`UnknownMediaIdException` is raised.
        """
        if self.videos.id_exists(media_id):
            media = self.videos.from_id(media_id)
            media.populate(fields)
            return media

        if self.images.id_exists(media_id):
            media = self.images.from_id(media_id)
            media.populate(fields)
            return media

        raise UnknownMediaIdException(f"The type of ID '{media_id}' could not be found")


class UnknownMediaIdException(Exception):
    """
    Raised when a media ID cannot be resolved to a Video or Image.
    """

    pass
