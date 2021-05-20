from FLIR.conservator.fields_manager import FieldsManager


class FieldsRequest:
    """
    A collection of fields to include in a query. Many different
    API calls will require specifying a list of fields using a :class:`FieldsRequest`.
    """

    def __init__(self, paths=None):
        if paths is None:
            paths = {}
        self.paths = paths
        self.excluded = set()

    @classmethod
    def create(cls, fields):
        """
        Create a `FieldsRequest`. Any function that accepts `fields` will
        eventually use this method to convert `fields` to a valid `FieldsRequest`.

        This accepts a variety of types:

        Pass through:

            >>> assert isinstance(fields_request, FieldsRequest)
            >>> FieldsRequest.create(fields_request)

        A single field::

            >>> FieldsRequest.create("name")

        A list of fields::

            >>> FieldsRequest.create(["name", "owner", "url"])

        A dictionary of fields, to include and exclude fields::

            >>> FieldsRequest.create({"name": True, "owner": True, "url": False})

        If a key's value is a dictionary, it is used as arguments to query that fields::

            >>> FieldsRequest.create({"frames": {"page": 0, "limit": 100}})

        This is the only way to add arguments to a field.

        These examples only demonstrate immediate child fields on an object. You may
        also specify subfields using a period (`.`) as a separator::

            >>> FieldsRequest.create("children.name")

        If one of the fields in a subpath needs arguments, it must be explicitly listed::

            >>> FieldsRequest.create({"frames.url" : True, "frames": {"page": 0, "limit": 100}})

        If no fields are included in a request, the field listed in
        :class:`~FLIR.conservator.fields_manager.FieldsManager` will be requested.
        This applies to subfields--so in the following example, the default fields of Video
        will be requested::

            >>> FieldsRequest.create(["name", "videos"])

        But, if at least one subfield is requested, only that field will be requested and the
        defaults will be ingored::

            >>> FieldsRequest.create(["name", "videos.name"])

        The same logic applies to the root object. If no specific fields are included,
        the default fields defined in :class:`~FLIR.conservator.fields_manager.FieldsManager` are included.
        Care must be taken when defining default fields that no circular type dependencies are created.

        Excluded fields (falsey dict values) override included fields, but do not affect defualt fields
        at this time. Please submit an issue if you need to exclude default fields. Including specific fields
        should always be preferred to relying on defaults.

        Note: This design mirrors `SGQLC's field selection syntax`_
         (specifically see ``__fields__``).

        .. _SGQLC's field selection syntax: https://sgqlc.readthedocs.io/en/latest/sgqlc.operation.html#selecting-to-generate-queries
        """
        if isinstance(fields, FieldsRequest):
            return fields
        if fields is None or fields == "":
            fields = {}
        if isinstance(fields, str):
            fields = [fields]
        if (
            isinstance(fields, list)
            or isinstance(fields, tuple)
            or isinstance(fields, set)
        ):
            fields = {name: True for name in fields}

        assert isinstance(fields, dict)

        return FieldsRequest(fields)

    def include(self, *field_path):
        """Includes `field_path` in the request."""
        self.include_fields(field_path)

    def exclude(self, *field_path):
        """Excludes `field_path` from the request."""
        self.exclude_fields(field_path)

    def include_field(self, *field_path):
        """Includes `field_path` in the request."""
        self.include_fields(field_path)

    def exclude_field(self, *field_path):
        """Excludes `field_path` from the request."""
        self.exclude_fields(field_path)

    def include_fields(self, field_paths):
        """Includes `field_paths` in the request."""
        for path in field_paths:
            self.paths[path] = True

    def exclude_fields(self, field_paths):
        """Excludes `field_paths` from the request."""
        self.excluded = self.excluded.union(field_paths)

    def prepare_query(self, query_selector):
        # TODO: account for exclusions in default fields
        for excluded in self.excluded:
            self.paths[excluded] = False

        # start by adding all requested fields
        all_selectors = []
        for path, value in self.paths.items():
            if value is False or value is None:
                # excluded field
                continue
            field = self.get_attr_by_path(path, query_selector)
            all_selectors.append((path, field))
            if value is True:
                field()
            if isinstance(value, dict):
                field(**value)

        # selectors that dont have any child nodes call them
        # this is not a smart way of doing this
        leaf_selectors = []
        for path, selector in all_selectors:
            # a selector is a leaf if no other selectors are
            # included below it
            for other_path, _ in all_selectors:
                if is_subfield_of(path, other_path):
                    # has a subfield selector--not a leaf
                    break
            else:
                # no leaf found
                leaf_selectors.append(selector)

        # if no fields are selected, select defaults on query
        if len(leaf_selectors) == 0:
            leaf_selectors.append(query_selector)

        # add default fields to all leafs:
        for leaf in leaf_selectors:
            FieldsManager.select_default_fields(leaf)

    def get_attr_by_path(self, path, obj):
        cur_path = ""
        for subpath in path.split("."):
            id_field = cur_path + "id"
            if hasattr(obj, "id") and self.paths.get(id_field, True):
                obj.id()
            obj = getattr(obj, subpath)
            cur_path += subpath + "."
        return obj


def is_subfield_of(parent, subpath):
    # parent : videos.frames.annotations
    # subpath: videos.frames.annotations.bbox.w
    # returns: True
    if subpath.startswith(parent):
        return len(subpath) > len(parent) and subpath[len(parent)] == "."
    return False
