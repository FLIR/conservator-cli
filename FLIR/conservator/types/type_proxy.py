import functools

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

    When you attempt to access a field, we first check that it exists on the
    underlying instance. If it doesn't, an `AttributeError` will be raised. If
    it does exists, we check to see if its type has a known :class:`TypeProxy`
    subclass. If it does, a type-proxied instance is returned, otherwise the base
    SGQLC type is returned. This lookup is compatible with optional and list types.

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
        if item in self._initialized_fields:
            field = self._instance._ContainerTypeMeta__fields[item]
            value = getattr(self._instance, item)

            return TypeProxy.wrap_instance(self._conservator, field.type, value)

        raise AttributeError

    def has_field(self, path):
        """Returns `True` if the current instance has initialized the specified `path`.
        
        This is frequently used to test if a call to `populate` is required, or to
        verify that a `populate` call worked."""
        obj = self
        if isinstance(obj, list):
            if len(obj) == 0:
                return True
            obj = obj[0]
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
                    break
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

    @staticmethod
    def has_base_type(base_type, type_):
        """Returns `True` if `type_` extends `base_type` in the
        SGQLC type hierarchy.

        For instance, a `[Collection]` has base type `Collection`."""
        b = type_
        while hasattr(b, "__base__"):
            if b == base_type:
                return True
            b = b.__base__
        return False

    @staticmethod
    def get_wrapping_type(type_):
        """Gets the :class:`TypeProxy` with an `underlying_type`
        related to `type_`. If one doesn't exist, returns `None`."""
        # rather hacky
        cls = None
        for subcls in TypeProxy.__subclasses__():
            if TypeProxy.has_base_type(subcls.underlying_type, type_):
                cls = subcls
        return cls

    @staticmethod
    def wrap_instance(conservator, type_, instance):
        """Creates a new TypeProxy instance of the appropriate
        subclass, if one exists."""
        # rather hacky
        cls = TypeProxy.get_wrapping_type(type_)
        if cls is None:
            # no warping type exists
            return instance
        if isinstance(instance, list):
            return [cls(conservator, i) for i in instance]
        return cls(conservator, instance)


class MissingFieldException(Exception):
    """Raised when a field can't be populated, but is required for an
    operation."""
    pass


def requires_fields(*fields):
    """Require `fields` for an instance method. If missing, calls
    `populate`. If `populate` fails, raises `MissingFieldException`."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            fr = FieldsRequest(include_fields=fields)
            self.populate(fr)
            for field in fields:
                if not self.has_field(field):
                    raise MissingFieldException(f"Missing required field '{field}'")
            return f(self, *args, **kwargs)
        return wrapper
    return decorator
