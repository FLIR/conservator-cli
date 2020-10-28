from conservator.connection import ConservatorGraphQLServerError
from conservator.types.type_proxy import TypeProxy


class SearchableType(TypeProxy):
    @classmethod
    def search(cls, conservator, **kwargs):
        results = cls.do_search(conservator, **kwargs)
        return list(map(lambda r: cls(conservator, r), results))

    @classmethod
    def do_search(cls, conservator, fields=(), **kwargs):
        try:
            fields = cls.always_fields + tuple(fields)
            results = conservator.query(cls.search_query,
                                        include_fields=fields,
                                        exclude_fields=cls.problematic_fields,
                                        **kwargs)
            return results
        except ConservatorGraphQLServerError as e:
            # Some errors are recoverable.
            # If it isn't, the handler will re-raise the exception.
            cls.handle_query_error(e)
            return cls.do_search(conservator, fields, **kwargs)
