class TypeManager:
    """
    Base Manger class.

    :param conservator: Conservator instance to use for queries.
    :param underlying_type: Underlying TypeProxy class to wrap.
    """

    def __init__(self, conservator, underlying_type):
        self._conservator = conservator
        self._underlying_type = underlying_type

    def from_id(self, id_):
        """
        Creates a new instance of `underlying_type` from an ID.
        """
        return self._underlying_type.from_id(self._conservator, id_)

    def from_json(self, json):
        """
        Return a wrapped instance from a dictionary (usually produced by calling
        :meth:``~TypeProxy.to_json``). The ID should be included for the returned
        instance to be useful.
        """
        return self._underlying_type.from_json(self._conservator, json)
