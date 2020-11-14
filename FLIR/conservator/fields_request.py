class FieldsRequest:
    """
    A collection of fields to include (or exclude) in a query. Many different
    API calls will require specifying a list of fields using a :class:`FieldsRequest`.

    It can be used with :class:`FLIR.conservator.connection.Connection.query`::
        >>> conservator = Conservator.default()
        >>> fields = FieldsRequest()
        >>> fields.include_field("id", "name")
        >>> datasets = conservator.query(Query.datasets, fields=fields, search_text="ADAS")
        >>> for dataset in datasets:
        ...     print(dataset.name)

    As used in this module, a `field_path` can refer to either:
        - A single field, like `"name"` to select `Project.name`
        - An entire subfield, like `"repository"` select all fields in `Dataset.reposistory`
        - A path to a field/subfield in a subfield, like `"repository.master"`
          to select the `Reposistory.master` field in `Dataset.reposistory`

    These paths can be as long/specific as you want.

    :param include_fields: List of field paths to include in the returned object(s).
        Fields of subtypes can be specified as a path separated by ``.``.  For instance,
        when querying for a Dataset, you could add ``repository.master`` to only
        include the ``master`` field of ``Dataset.repository``.
        If empty or not specified, all fields will be included.
    :param exclude_fields: A list of field paths to exclude. These take the same form as
        included fields, and override them. In the above example, excluding ``repository``
        will exclude all fields of ``repository``.
    :param depth: Max depth for requested fields. Defaults to the maximum depth of any
        included field, plus 1.
    """
    def __init__(self, include_fields=("",), exclude_fields=(), depth=None):
        self.included = set(include_fields)
        self.excluded = set(exclude_fields)
        self._depth = depth

    @property
    def depth(self):
        if self._depth is not None:
            return self._depth
        max_depth = max(map(lambda f: f.count("."), self.included))
        return max_depth + 1

    def set_depth(self, depth):
        self._depth = depth

    def add_fields_to_request(self, obj, current_path="", current_depth=0):
        """
        Adds fields to an SGQLC object (usually initially called with an operation).

        :param obj: The SGQLC object to add fields to.
        :param current_path: The current path, used to filter included and excluded path fields.
        :param current_depth: How many times this has been called recursively.
        """
        if current_depth > self.depth:
            return

        field_names = [name for name in dir(obj) if not name.startswith("_")]
        if len(field_names) == 0:
            # Fields are included in a query by calling them.
            # View the SGQLC docs for more info.
            obj()
            return

        path_prefix = ("" if current_path == "" else current_path + ".")

        for field_name in field_names:
            field_path = path_prefix + field_name
            if self.should_include_path(field_path):
                field = obj[field_name]
                self.add_fields_to_request(field, field_path, current_depth + 1)

    def should_include_path(self, path):
        """Returns `True` if this request should include `path`."""
        # if excluded, definitely no
        if path in self.excluded:
            return False

        # if it or a child path is included, yes
        for included in self.included:
            if included.startswith(path) or path.startswith(included):
                return True
        return False

    def include_field(self, *field_path):
        """Includes `field_path` in the request."""
        self.include_fields(field_path)

    def exclude_field(self, *field_path):
        """Excludes `field_path` from the request."""
        self.exclude_fields(field_path)

    def include_fields(self, field_paths):
        """Includes `field_paths` in the request."""
        if "" in self.included:
            self.included.remove("")
        self.included = self.included.union(field_paths)

    def exclude_fields(self, field_paths):
        """Excludes `field_paths` from the request."""
        self.excluded = self.excluded.union(field_paths)

