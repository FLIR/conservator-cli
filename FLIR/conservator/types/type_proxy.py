from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.util import to_clean_string


class TypeProxy(object):
    """
    Wraps an SGQLC object of a specific type with a known ``id``.

    Subclasses can add class and instance methods to add functionality.

    Fields of the underlying instance can be accessed on this instance,
    and additional fields can be requested using :func:`~TypeProxy.populate`, which
    uses the underlying ``by_id_query``. For this reason, all instances must
    also have a reference to a :class:`~FLIR.conservator.conservator.Conservator` instance.

    :param conservator: The instance of :class:`~FLIR.conservator.conservator.Conservator`
        that created the underlying instance.
    :param instance: The SGQLC object to wrap, usually returned by running
        some query.
    """
    underlying_type = None
    by_id_query = None

    def __init__(self, conservator, instance):
        self._conservator = conservator
        self._instance = instance
        self._initialized_fields = [field for field in instance]

    def __getattr__(self, item):
        value = getattr(self._instance, item)

        if item in self._initialized_fields:
            return value

        raise AttributeError

    def has_field(self, path):
        """Returns `True` if the current instance has initialized the specified `path`.
        
        This is frequently used to test if a call to `populate` is required, or to
        verify that a `populate` call worked."""
        obj = self
        for field in path.split("."):
            if not hasattr(obj, field):
                return False
            obj = getattr(obj, field)
        return True

    def populate_all(self):
        """Query conservator for all missing fields."""
        self.populate(fields=FieldsRequest())

    def populate(self, fields=None):
        """Query conservator for the specified fields."""
        if self.by_id_query is None:
            raise NotImplementedError

        if fields is None:
            fields = FieldsRequest()
        else:
            needs_new_fields = False
            for field in fields.included:
                if not self.has_field(field):
                    needs_new_fields = True
            if not needs_new_fields:
                return

        result = self._conservator.query(self.by_id_query, id=self.id, fields=fields)
        for field in result:
            v = getattr(result, field)
            setattr(self._instance, field, v)
            self._initialized_fields.append(field)

    @classmethod
    def from_id(cls, conservator, id_):
        """Create a proxied instance from an ID. The underlying type
        of the class should match the type of the ID."""
        base_item = cls.underlying_type({"id": id_})
        return cls(conservator, base_item)

    def __str__(self):
        return f"{self.underlying_type}\n{to_clean_string(self)}"

