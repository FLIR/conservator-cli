"""
Conservator sends Dates as an integer, but SGQLC expects
them to be strings. So, we override the default Date type
with this custom one.
"""

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
