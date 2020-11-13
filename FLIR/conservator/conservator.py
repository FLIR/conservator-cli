from FLIR.conservator.config import Config
from FLIR.conservator.connection import ConservatorConnection
from FLIR.conservator.managers import ProjectsManager


class Conservator(ConservatorConnection):
    """
    :class:`Conservator` is the highest level class of this library. It will likely be the
    starting point for all queries and operations.

    You can get an instance using the default :class:`Config`::
        >>> Conservator.default()
        <Conservator at https://flirconservator.com>

    You can create also create an instance by passing any :class:`Config`
    object::
        >>> config = Config(my_email, my_key, "https://localhost:3000")
        >>> Conservator(config)
        <Conservator at https://localhost:3000>

    :param config: The :class:`FLIR.conservator.config.Config` object to use for this connection.
    """
    def __init__(self, config):
        super().__init__(config)
        self.projects = ProjectsManager(self)

    def __repr__(self):
        return f"<Conservator at {self.config.url}>"

    @staticmethod
    def default():
        """
        Returns a :class:`Conservator` using :func:`FLIR.conservator.config.Config.default`.
        """
        return Conservator(Config.default())
