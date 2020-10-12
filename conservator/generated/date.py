from sgqlc.types import Scalar


class Date(Scalar):

    @classmethod
    def converter(cls, s):
        return int(s)

    @classmethod
    def __to_json_value__(cls, value):
        if value is None:
            return None
        return str(value)
