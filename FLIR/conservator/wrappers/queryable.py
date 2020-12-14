from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.wrappers import TypeProxy


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
        """Query conservator for the specified fields."""
        if isinstance(fields, list):
            fields = FieldsRequest(include_fields=tuple(fields))
        elif isinstance(fields, str):
            fields = FieldsRequest(include_fields=(fields,))

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

        result = self._populate(fields)
        if result is None:
            return
        for field in result:
            v = getattr(result, field)
            setattr(self._instance, field, v)
            self._initialized_fields.append(field)

    def _populate(self, fields):
        if self.by_id_query is None:
            raise NotImplementedError
        return self._conservator.query(self.by_id_query, id=self.id, fields=fields)
