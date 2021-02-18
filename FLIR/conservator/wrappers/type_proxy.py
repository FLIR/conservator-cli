import functools

import sgqlc.types

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.util import to_clean_string


class TypeProxy(object):
    """
    Wraps an SGQLC object. Fields of the underlying instance can be accessed on this
    instance. Subclasses can add class and instance methods to add functionality.

    When you attempt to access a field, we first check that it exists on the
    underlying instance. If it doesn't, an `AttributeError` will be raised.

    If it does exists, we check to see if a subclass of :class:`TypeProxy` is defined
    with a matching ``underlying_type``. If it does, an instance of that subclass is
    returned with the value. Otherwise, a instance of the generic :class:`TypeProxy`
    is returned. This ensures all values returned by queries have the same basic methods
    (like :meth:`TypeProxy.to_json`). The type look-up is compatible with optional and
    list types.

    Instances should be created using :func:`TypeProxy.wrap`, which will use the
    appropriate class and constructor.

    :param conservator: The instance of :class:`~FLIR.conservator.conservator.Conservator`
        that created the underlying instance.
    :param instance: The SGQLC object to wrap, usually returned by running some query.
    """

    underlying_type = None

    def __init__(self, conservator, instance):
        if isinstance(instance, TypeProxy):
            # Before queries returned a TypeProxy, many methods had to
            # wrap the raw type manually. This ensures any old scripts
            # will not break.
            self._conservator = instance._conservator
            self._instance = instance._instance
            self.underlying_type = instance.underlying_type
            self._initialized_fields = instance._initialized_fields
            return

        self._conservator = conservator
        self._instance = instance
        if self.underlying_type is None:
            self.underlying_type = instance.__class__
        self._initialized_fields = [field for field in instance]

    def __getattr__(self, field_name):
        if field_name in self._initialized_fields:
            field = self._instance._ContainerTypeMeta__fields[field_name]
            value = getattr(self._instance, field_name)

            return TypeProxy.wrap(self._conservator, field.type, value)

        raise AttributeError(f"Unknown or uninitialized attribute: '{field_name}'")

    def has_field(self, path):
        """Returns `True` if the current instance has initialized the specified `path`.

        This is frequently used to test if a call to `populate` is required, or to
        verify that a `populate` call worked."""
        obj = self
        for field in path.split("."):
            if isinstance(obj, list):
                if len(obj) == 0:
                    return True
                obj = obj[0]
            if not hasattr(obj, field):
                return False
            obj = getattr(obj, field)
        return True

    @classmethod
    def from_id(cls, conservator, id_):
        """Return a wrapped instance from an ID. The underlying type
        of the class should match the type of the ID.

        This does not populate any fields besides ``id``. You must call
        :meth:`~FLIR.conservator.wrappers.queryable.QueryableType.populate`
        on the returned instance to populate any fields.

        .. note:: Use :meth:`~FLIR.conservator.managers.type_manager.TypeManager.id_exists`
           to verify that an ID is correct. Otherwise an :class:`~FLIR.conservator.wrappers.queryable.InvalidIdException` may
           be thrown on later operations.
        """
        return cls.from_json(conservator, {"id": id_})

    @classmethod
    def from_json(cls, conservator, json):
        """
        Return a wrapped instance from a dictionary (usually produced by calling
        :meth:`~TypeProxy.to_json`). The ID should be included for the returned
        instance to be useful.
        """
        base_item = cls.underlying_type(json)
        return cls(conservator, base_item)

    def to_json(self):
        """
        Returns the underlying instance as a dictionary, suitable for turning
        into JSON.
        """
        return self._instance.__to_json_value__()

    def __to_json_value__(self):
        # This is added for backwards compatibility to scripts that may have been
        # using this method on unwrapped instances. It's undocumented to avoid confusion.
        return self._instance.__to_json_value__()

    def __str__(self):
        return to_clean_string(self)

    @staticmethod
    def has_base_type(base_type, type_):
        """
        Returns `True` if `type_` extends `base_type` in the SGQLC type hierarchy.

        For instance, a ``[Collection]`` has base type ``Collection``.
        """
        b = type_
        while hasattr(b, "__base__"):
            if b == base_type:
                return True
            b = b.__base__
        return False

    @staticmethod
    def get_wrapping_type(type_):
        """
        Gets the :class:`TypeProxy` subclass with an `underlying_type`
        related to `type_`. If one doesn't exist, returns generic :class:`TypeProxy`.

        This checks the base type. For instance, it will match ``[Video]!`` with ``Video``.
        """
        # rather hacky
        for subcls in all_subclasses(TypeProxy):
            if TypeProxy.has_base_type(subcls.underlying_type, type_):
                return subcls
        return TypeProxy

    @staticmethod
    def wrap(conservator, type_, instance):
        """
        Creates a new :class:`TypeProxy` instance of the appropriate subclass, or a generic
        if no subclass exists for the type. Scalar types, such as `None`, `str`, `bool`, etc.,
        are not wrapped and returned as-is.

        :param conservator: Conservator instance tied to the instance. Subclasses use this for
            many instance methods.
        :param type_: The SGQLC type of the instance to wrap.
        :param instance: The SGQLC object to wrap.
        """
        unwrapped_types = (
            type(None),
            str,
            int,
            float,
            bool,
        )
        if isinstance(instance, unwrapped_types):
            return instance

        if isinstance(instance, list):
            # This isn't the most efficient method, as it recalculates type for each item,
            # but it handles nested lists correctly... We can refactor if speed ever
            # becomes a concern.
            return ListTypeProxy(
                TypeProxy.wrap(conservator, type_, item) for item in instance
            )

        if isinstance(instance, sgqlc.types.ContainerType) and len(instance) == 0:
            # No fields were initialized, meaning the value is likely None.
            return None

        cls = TypeProxy.get_wrapping_type(type_)
        return cls(conservator, instance)


class ListTypeProxy(list):
    """
    Identical to built-in `list`, except it provides :meth:`to_json`. This ensures all types
    returned by queries have a :meth:`to_json`.
    """

    def to_json(self):
        """
        Returns a `list` suitable for turning into JSON.
        """
        return [
            item.to_json() if isinstance(item, TypeProxy) else item for item in self
        ]


class MissingFieldException(Exception):
    """Raised when a field can't be populated, but is required for an
    operation."""

    pass


def requires_fields(*fields):
    """
    Decorator for requiring `fields` for an instance method. If missing, calls
    `populate`. If `populate` fails, raises `MissingFieldException`.

    This should be used on any instance method that requires certain fields to
    function correctly.

    :param fields: Strings containing the names of required fields. They can be
        subfields (such as "repository.master" on a Dataset).
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            fr = FieldsRequest.create(fields)
            if hasattr(self, "populate"):
                self.populate(fr)
            for field in fields:
                if not self.has_field(field):
                    raise MissingFieldException(f"Missing required field '{field}'")
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
