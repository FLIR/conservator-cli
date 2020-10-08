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
from conservator.stats import ConservatorStats


class Conservator(ConservatorConnection):

    def __init__(self, credentials, url="https://flirconservator.com"):
        """
        :param credentials: The :class:`Credentials` object to use for this connection.
        :param url: The URL of your conservator instance.
        """
        super().__init__(credentials, url)
        self.stats = ConservatorStats(self)

    def __repr__(self):
        return f"<Conservator at {self.url}>"


