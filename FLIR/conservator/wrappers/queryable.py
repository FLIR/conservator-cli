from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.wrappers import TypeProxy


class InvalidIdException(Exception):
    pass


class QueryableType(TypeProxy):
    """
    Adds :func:``populate`` for querying and populating additional fields.

    Subclasses must define ``by_id_query`` to be a query that can
    return more fields of the type given an id. Alternatively, they may define
    a custom ``_populate`` if the method of querying varies.
    """

    by_id_query = None

    def populate_all(self):
        """Query conservator for all missing fields."""
        self.populate(fields=FieldsRequest())

    def populate(self, fields=None):
        """
        Query conservator for the specified fields, even if they
        already exist on the object.

        To filter existing fields, use `requires_fields`
        """

        fields = FieldsRequest.create(fields)

        result = self._populate(fields)
        if result is None:
            raise InvalidIdException(f"Query with id='{self.id}' returned None")
        for field in result:
            v = getattr(result, field)
            setattr(self._instance, field, v)
            self._initialized_fields.append(field)

    def _populate(self, fields):
        if self.by_id_query is None:
            raise NotImplementedError
        return self._conservator.query(self.by_id_query, id=self.id, fields=fields)
