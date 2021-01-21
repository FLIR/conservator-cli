from FLIR.conservator.wrappers.queryable import InvalidIdException


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
        except InvalidIdException:
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
        return self._underlying_type.from_id(self._conservator, id_)

    def from_json(self, json):
        """
        Return a wrapped instance from a dictionary (usually produced by calling
        :meth:`~TypeProxy.to_json`). The ID should be included for the returned
        instance to be useful.
        """
        return self._underlying_type.from_json(self._conservator, json)
