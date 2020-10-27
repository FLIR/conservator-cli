from conservator.types.type_proxy import TypeProxy


class SearchableType(TypeProxy):
    @classmethod
    def query(cls, conservator, **kwargs):
        results = cls.do_query(conservator, **kwargs)
        return list(map(lambda r: cls(conservator, r), results))

    @classmethod
    def do_query(cls, conservator, fields=(), **kwargs):
        try:
            unfiltered_fields = cls.always_fields + tuple(fields)
            requested_fields = tuple(filter(lambda f: f not in cls.problematic_fields, unfiltered_fields))
            results = conservator.query(cls.search_query,
                                        fields=requested_fields,
                                        **kwargs)
            return results
        except ConservatorGraphQLServerError as e:
            # Some errors are recoverable.
            # If it isn't, the handler will re-raise the exception.
            cls.handle_query_error(e)
            return cls.do_query(conservator, fields, **kwargs)
