from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.wrappers import TypeProxy


class InvalidIdException(Exception):
    """
    Raised when a query fails due to an invalid ID.
    """


class QueryableType(TypeProxy):
    """
    Adds :meth:`populate` for querying and populating additional fields.

    Subclasses must define ``by_id_query`` to be a query that can
    return more fields of the type given an id. Alternatively, they may define
    a custom ``_populate`` method if the method of querying is unique.
    """

    by_id_query = None

    def populate_all(self):
        """Query conservator for all missing fields."""
        self.populate(fields=FieldsRequest())

    def populate(self, fields=None):
        """
        Query conservator for the specified fields, even if they
        already exist on the object.

        To filter existing fields, use :func:`~FLIR.conservator.wrappers.type_proxy.requires_fields`
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
