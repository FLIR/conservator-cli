from FLIR.conservator.fields_request import FieldsRequest


class PaginatedQuery:
    """
    Enables pagination of any query with ``page`` and ``limit`` arguments.

    Assume you want to iterate through all the Projects in a project search
    query. You could do something like the following::
        >>> results = PaginatedQuery(conservator, Project, Query.projects, search_text="ADAS")
        >>> results = results.including_fields("name")
        >>> for project in results:
        ...     print(project.name)

    """
    def __init__(self, conservator, underlying_type, query, base_operation=None,
                 fields=None, page_size=100,
                 **kwargs):
        self._conservator = conservator
        self._underlying_type = underlying_type
        self._query = query
        self._base_operation = base_operation
        if fields is None:
            fields = FieldsRequest()
        self.fields = fields
        self._page = 0
        self._limit = page_size
        self.results = []
        self.kwargs = kwargs
        self.started = False
        self.done = False

    def with_fields(self, fields):
        """Sets the query's :class:`~FLIR.conservator.fields_request.FieldsRequest` to `fields`."""
        if self.started:
            raise ConcurrentQueryModificationException()
        self.fields = fields
        return self

    def including_fields(self, *fields):
        """
        :param fields: Fields to include in the results.
        """
        if self.started:
            raise ConcurrentQueryModificationException()
        if len(fields) == 0:
            return self.including_all_fields()
        self.fields.include_fields(fields)
        return self

    def excluding_fields(self, *fields):
        """
        :param fields: Fields to exclude in the results.
        """
        if self.started:
            raise ConcurrentQueryModificationException()
        self.fields.exclude_fields(fields)
        return self

    def including_all_fields(self):
        """
        Include all non-excluded fields in the results.
        """
        if self.started:
            raise ConcurrentQueryModificationException()
        if self.started:
            raise
        self.fields.include_field("")
        return self

    def first(self):
        """
        Returns the first result.
        """
        if len(self.results) > 0:
            return self.results[0]
        first = self._do_query(page=0, limit=1)[0]
        return first

    def _do_query(self, page, limit):
        results = self._conservator.query(self._query, self._base_operation,
                                          self.fields,
                                          page=page,
                                          limit=limit,
                                          **self.kwargs)
        return [self._underlying_type(self._conservator, i) for i in results]

    def _next_page(self):
        self.started = True
        results = self._do_query(self._page, self._limit)
        self._page += 1
        return results

    def __iter__(self):
        for item in self.results:
            yield item

        while not self.done:
            next_page = self._next_page()
            for item in next_page:
                self.results.append(item)
                yield item
            if len(next_page) < self._limit:
                self.done = True
                return

    def __len__(self):
        return len(list(self.__iter__()))


class ConcurrentQueryModificationException(Exception):
    """
    Raised when a paginated query is modified in the middle
    of its execution.
    """
    # TODO: Allow modifying queries in progress.
    pass
