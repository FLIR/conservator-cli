import operator

from FLIR.conservator.fields_request import FieldsRequest


class PaginatedQuery:
    """
    Enables pagination of any query with ``page`` and ``limit`` arguments.

    Assume you want to iterate through all the Projects in a project search
    query. You could do something like the following:

    >>> results = PaginatedQuery(conservator, query=Query.projects, search_text="ADAS")
    >>> results = results.including("name")
    >>> for project in results:
    ...     print(project.name)

    :param conservator: The conservator instance to query.
    :param wrapping_type: Not required. Included for backwards-compatibility.
    :param query: The GraphQL Query to use.
    :param base_operation: Not required. Included for backwards-compatibility.
    :param fields: Fields to include in the returned objects.
    :param page_size: The page size to use when submitting requests.
    :param unpack_field: If specified, instead of directly returning the resulting object(s) from a query,
        returns the specified field. For instance, the query ``Query.dataset_frames_only`` is paginated, but
        returns a non-iteratable ``DatasetFrames`` object. The list of ``DatasetFrame`` is stored under the
        "dataset_frames" field. So if querying this, we'd want to set `unpack_field` to "dataset_frames".
    :param reverse: If True, query for results in reverse order.  Intended for
        certain API calls that return results in a fixed order, e.g. dataset
        frames.  The capability to grab frames in reverse order may make the
        collection of the newest items much more efficient.  Requires the
        `total_unpack_field` to be set.
    :param total_unpack_field: If `reverse` is true, the query fields need to
        include a field containing the total number of entries.  Supply the
        field name to this parameter.
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
        reverse=False,
        total_unpack_field=None,
        **kwargs,
    ):
        # Unfortunately, query is a required arg, but for backwards-compatibility reasons can't be made required.
        assert query is not None
        self._conservator = conservator
        self._query = query
        self.fields = FieldsRequest.create(fields)
        self._page = 0
        self._limit = page_size
        self.unpack_field = unpack_field
        self.results = []
        self.reverse = reverse
        self._total_items = 0
        if reverse:
            if not total_unpack_field:
                raise KeyError(
                    f"total_unpack_field must be supplied if reverse is True"
                )
            self.fields.include_field(total_unpack_field)
            # Perform a single-entry query to collect the total count of items.
            try:
                results = self._conservator.query(
                    query=self._query, fields=self.fields, page=1, limit=1, **kwargs
                )
            except AttributeError as exc:
                if str(exc).endswith(total_unpack_field):
                    raise KeyError(total_unpack_field)
                raise
            self._total_items = getattr(results, total_unpack_field)
            if self._limit > self._total_items:
                self._limit = self._total_items
                # Don't confuse the API.
                if self._limit == 0:
                    self._limit = 1
            # Set the page number to the last page of results.
            if self._total_items > self._limit:
                self._page = self._total_items // self._limit
                if self._total_items % self._limit:
                    # Count any partial page.
                    self._page += 1
                # Page numbers are 0-based.
                self._page -= 1

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

        self.including(*kwargs.keys())

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
        self.fields = FieldsRequest.create(fields)
        return self

    def including(self, *fields):
        """
        :param fields: Fields to include in the results.
        """
        return self.including_fields(*fields)

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

    def excluding(self, *fields):
        """
        :param fields: Fields to exclude in the results.
        """
        return self.excluding_fields(*fields)

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
        self.fields = FieldsRequest.create(None)
        return self

    def page_size(self, page_size):
        """
        Set the number of items to request in each query.

        Typically, larger values will make the overall execution faster,
        but individual requests may be large and slow.
        """
        if self.started:
            raise ConcurrentQueryModificationException()
        self._limit = page_size
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
            query=self._query, fields=self.fields, page=page, limit=limit, **self.kwargs
        )
        return results

    def _next_page(self):
        self.started = True
        results = self._do_query(self._page, self._limit)
        if not self.reverse:
            self._page += 1
        else:
            self._page -= 1

        if results is None:
            return []
        if self.unpack_field is not None:
            results = getattr(results, self.unpack_field)
        if self.reverse and results:
            results = list(reversed(results))
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
            if self.reverse and self._page < 0:
                self.done = True
                return
            if not self.reverse and len(next_page) < self._limit:
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
