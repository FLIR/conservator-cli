import operator

from FLIR.conservator.fields_request import FieldsRequest


class PaginatedQuery:
    """
    Enables pagination of any query with ``page`` and ``limit`` arguments.

    Assume you want to iterate through all the Projects in a project search
    query. You could do something like the following:

    >>> results = PaginatedQuery(conservator, wrapping_type=Project, query=Query.projects, search_text="ADAS")
    >>> results = results.including_fields("name")
    >>> for project in results:
    ...     print(project.name)

    :param conservator: The conservator instance to query.
    :param wrapping_type: If specified, a :class:`~FLIR.conservator.wrappers.type_proxy.TypeProxy` class to
        wrap instances in before they are returned.
    :param query: The GraphQL Query to use.
    :param base_operation: If specified, the base type of the query. Defaults to ``Query``.
    :param fields: Fields to include in the returned objects.
    :param page_size: The page size to use when submitting requests.
    :param unpack_field: If specified, instead of directly returning the resulting object(s) from a query,
        returns the specified field. For instance, the query ``Query.dataset_frames_only`` is paginated, but
        returns a non-iteratable ``DatasetFrames`` object. The list of ``DatasetFrame`` is stored under the
        "dataset_frames" field. So if querying this, we'd want to set `unpack_field` to "dataset_frames".
    """

    def __init__(
        self,
        conservator,
        wrapping_type=None,
        query=None,
        base_operation=None,
        fields=None,
        page_size=25,
        unpack_field=None,
        **kwargs
    ):
        assert query is not None  # Unfortunately, this is a required arg, but
        # for legacy reasons can't be moved before "wrapping_type" and made required.
        self._conservator = conservator
        self._wrapping_type = wrapping_type
        self._query = query
        self._base_operation = base_operation
        if fields is None:
            fields = FieldsRequest()
        self.fields = fields
        self._page = 0
        self._limit = page_size
        self.unpack_field = unpack_field
        self.results = []
        self.kwargs = kwargs
        self.started = False
        self.done = False
        self.filters = []

    def filtered_by(self, func=operator.eq, **kwargs):
        """
        Filter results by field value.

        For example, to verify that

        :param func: A function to use to compare an instance's `field`
            with the provided `value`. If it returns `False` for any
            field, the instance will be skipped when returning results.
        :param kwargs: A list of field name-value pairs to pass through
            the filter function for each instance.
        """

        def filter_(instance):
            for field_name, filter_value in kwargs.items():
                if not hasattr(instance, field_name):
                    return False
                field_value = getattr(instance, field_name)
                if not func(field_value, filter_value):
                    return False
            return True

        self.filters.append(filter_)
        return self

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
        Returns the first result, or `None` if it doesn't exist.
        """
        if self.started:
            # don't mess with limits or pages
            for item in self:
                return item
            return None
        # otherwise set limit to 1
        original_limit = self._limit
        self._limit = 1
        try:
            for item in self:
                return item
            return None
        finally:
            self._limit = original_limit

    def _do_query(self, page, limit):
        results = self._conservator.query(
            self._query,
            self._base_operation,
            self.fields,
            page=page,
            limit=limit,
            **self.kwargs
        )
        if results is None:
            return []
        if self.unpack_field is not None:
            results = getattr(results, self.unpack_field)
        if self._wrapping_type is None:
            return results
        return [self._wrapping_type(self._conservator, i) for i in results]

    def _next_page(self):
        self.started = True
        results = self._do_query(self._page, self._limit)
        self._page += 1
        return results

    def _passes_filters(self, instance):
        return all(filter_(instance) for filter_ in self.filters)

    def __iter__(self):
        for item in self.results:
            yield item

        while not self.done:
            next_page = self._next_page()
            for item in next_page:
                if self._passes_filters(item):
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