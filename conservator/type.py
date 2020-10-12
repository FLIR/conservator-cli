import abc
import functools

from conservator.connection import ConservatorGraphQLServerError, ConservatorMalformedQueryException
from conservator.generated import schema
from conservator.util import to_python_field_name


class TypeProxy(abc.ABC):
    underlying_type = None
    by_id_query = None
    search_query = None
    problematic_fields = None
    always_fields = (
        'id',
    )

    def __init__(self, conservator, instance):
        self._conservator = conservator
        self._instance = instance
        self._initialized_fields = list(filter(lambda f: not f.startswith('_'),
                                               instance.__dict__))

    def __getattr__(self, item):
        value = getattr(self._instance, item)

        if item in self._initialized_fields:
            return value

        raise AttributeError

    def handle_query_error(self, e):
        for error in e.errors:
            if "Cannot return null for non-nullable field" in error["message"]:
                fields = filter(lambda i: isinstance(i, str), error["path"])
                problematic_field = list(fields)[1]
                name = to_python_field_name(self.underlying_type, problematic_field)
                if name not in self.problematic_fields:
                    print("Server encountered an error due to a null value for a non-nullable field.")
                    print("Attempting to resolve by excluding field in future queries.")
                    print("Excluded field:", name)
                    self.problematic_fields.append(name)
                continue

            # can't handle this error
            raise

    @classmethod
    def get_all_fields(cls):
        fields = []
        for field in cls.underlying_type:
            fields.append(field.name)
        return fields

    def populate_all(self):
        self.populate(self.get_all_fields())

    def populate(self, fields=()):
        if self.by_id_query is None:
            raise NotImplementedError
        try:
            request_fields = tuple(filter(lambda f: f not in self.problematic_fields, fields))
            result = self._conservator.query(self.by_id_query, id=self.id, fields=request_fields)
            for field in request_fields:
                v = getattr(result, field)
                setattr(self._instance, field, v)
                self._initialized_fields.append(field)
        except ConservatorGraphQLServerError as e:
            # Some errors are recoverable.
            # If it isn't, the handler will re-raise the exception.
            self.handle_query_error(e)
            self.populate(fields)

    @classmethod
    def from_id(cls, conservator, id_):
        base_item = cls.underlying_type({"id": id_})
        return cls(conservator, base_item)
        

class QueryableType(TypeProxy):
    @classmethod
    def query(cls, conservator, **kwargs):
        results = cls.do_query(conservator, **kwargs)
        return list(map(lambda r: cls(conservator, r), results))

    @classmethod
    def do_query(cls, conservator, fields=(), **kwargs):
        requested_fields = cls.always_fields + tuple(fields)
        results = conservator.query(cls.search_query,
                                    fields=requested_fields,
                                    **kwargs)
        return results


def create_queryable_type_from_name(name):
    assert name == name.lower()
    capitalized = name.capitalize()
    plural = name + "s"
    count = plural + "_query_count"
    return type(
        capitalized,
        (QueryableType,),
        {
            "underlying_type": getattr(schema, capitalized),
            "search_query": getattr(schema.Query, plural),
            "by_id_query": getattr(schema.Query, name),
            "count_query": getattr(schema.Query, count),
            "problematic_fields": [],
        }
    )


class Project(create_queryable_type_from_name("project")):
    @classmethod
    def query(cls, conservator, **kwargs):
        search_text = kwargs.get("search_text", "")
        # TODO: find out what other characters break projects queries
        bad_chars = ":?\\"
        for char in bad_chars:
            if char in search_text:
                raise ConservatorMalformedQueryException(f"You can't include '{char}' in a projects search string")
        return super(Project, cls).query(conservator, **kwargs)


class Dataset(create_queryable_type_from_name("dataset")):
    problematic_fields = ["shared_with"]


Video = create_queryable_type_from_name("video")
Collection = create_queryable_type_from_name("collection")

