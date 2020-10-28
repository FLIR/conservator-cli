from conservator.connection import ConservatorGraphQLServerError
from conservator.util import graphql_to_python


class TypeProxy(object):
    underlying_type = None
    by_id_query = None
    problematic_fields = None
    always_fields = ('id',)

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

    @classmethod
    def handle_query_error(cls, e):
        new_problematic_fields = cls.problematic_fields[:]
        for error in e.errors:
            if "Cannot return null for non-nullable field" in error["message"]:
                fields = tuple(filter(lambda i: isinstance(i, str), error["path"]))
                problematic_field = ".".join(map(graphql_to_python, fields[1:]))
                if problematic_field not in new_problematic_fields:
                    print("Server encountered an error due to a null value for a non-nullable field.")
                    print("Attempting to resolve by excluding field in future queries.")
                    print("Excluded field:", problematic_field)
                    new_problematic_fields.append(problematic_field)
                if problematic_field in cls.problematic_fields:
                    raise Exception(f"Field '{problematic_field}' was included despite being problematic.")
                continue

            # can't handle this error
            raise
        cls.problematic_fields = new_problematic_fields

    @classmethod
    def get_all_fields(cls):
        fields = []
        for field in cls.underlying_type:
            fields.append(field.name)
        return fields

    def populate_all(self):
        self.populate(self.get_all_fields())

    def filter_new_fields(self, fields):
        filtered = []
        for field in fields:
            if field not in self.problematic_fields and field not in self._initialized_fields:
                filtered.append(field)
        return filtered

    def populate(self, *args):
        fields = []
        for arg in args:
            if isinstance(arg, str):
                fields.append(arg)
            else:
                fields += list(arg)

        request_fields = self.filter_new_fields(fields)

        if len(request_fields) == 0:
            return

        if self.by_id_query is None:
            raise NotImplementedError
        try:
            result = self._conservator.query(self.by_id_query, id=self.id, include_fields=request_fields)
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
        

