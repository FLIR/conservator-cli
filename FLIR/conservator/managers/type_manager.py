from FLIR.conservator.connection import ConservatorGraphQLServerError

from FLIR.conservator.wrappers.queryable import InvalidIdException


class AmbiguousIdentifierException(Exception):
    def __init__(self, identifier):
        super().__init__(f"Multiple items found for '{identifier}', use ID")


class TypeManager:
    """
    Base Manger class.

    :param conservator: Conservator instance to use for queries.
    :param underlying_type: Underlying TypeProxy class to wrap.
    """

    def __init__(self, conservator, underlying_type):
        self._conservator = conservator
        self._underlying_type = underlying_type

    def id_exists(self, id_):
        """
        Returns `True` if the id is valid for the `underlying_type`.
        """
        instance = self.from_id(id_)
        try:
            instance.populate("id")
        except (InvalidIdException, ConservatorGraphQLServerError):
            return False
        return True

    def from_id(self, id_):
        """
        Creates a new instance of `underlying_type` from an ID.

        This does not populate any fields besides ``id``. You must call
        :meth:`~FLIR.conservator.wrappers.queryable.QueryableType.populate`
        on the returned instance to populate any fields.

        .. note:: Use :meth:`~FLIR.conservator.managers.type_manager.TypeManager.id_exists`
           to verify that an ID is correct. Otherwise an :class:`InvalidIdException` may
           be thrown on later operations.
        """
        if not self._conservator.is_valid_id(id_):
            raise InvalidIdException(id_)

        return self._underlying_type.from_id(self._conservator, id_)

    def from_json(self, json):
        """
        Return a wrapped instance from a dictionary (usually produced by calling
        :meth:`~TypeProxy.to_json`). The ID should be included for the returned
        instance to be useful.
        """
        return self._underlying_type.from_json(self._conservator, json)

    def from_string(self, string, fields=None):
        """
        This returns an instance from a string identifier.

        By default, it expects an ID, but subclasses can (and should)
        add alternative identifiers. For instance, collections can be
        identified by their path, so the collections manager should be
        checking if the identifier is a path.

        Invalid identifiers should raise helpful exceptions.
        """
        instance = self.from_id(string)
        instance.populate(fields)
        return instance
