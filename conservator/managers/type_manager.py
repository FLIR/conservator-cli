from conservator.types.type_proxy import TypeProxy


class TypeManager:
    def __init__(self, conservator, underlying_type):
        assert issubclass(underlying_type, TypeProxy)
        self.underlying_type = underlying_type
        self.conservator = conservator

    def from_id(self, idx, fields=(), all_fields=False):
        if all_fields:
            fields = self.underlying_type.get_all_fields()
        item = self.underlying_type.from_id(self.conservator, idx)
        item.populate(fields)
        return item
