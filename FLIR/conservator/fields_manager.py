import re
import keyword
from FLIR.conservator.generated import schema

class FieldsManager:
    """
    Stores a map of problematic fields for each SGQLC type. These
    are used during queries to avoid errors.
    """
    def __init__(self):
        self.problematic_fields = {
            schema.Video: {"shared_with"},
        }

    def get_problematic_paths(self, typ):
        """Get problematic field paths for a given SGQLC `type`"""
        return self.problematic_fields.get(typ, ())

    def add_problematic_path(self, typ, path):
        """Add a problematic field path for a given SGQLC `type`"""
        if self.problematic_fields.get(typ) is None:
            self.problematic_fields[typ] = set()
        self.problematic_fields[typ].add(path)

    re_camel_case_words = re.compile('([^A-Z]+|[A-Z]+[^A-Z]*)')

    @staticmethod
    def graphql_to_python(name):
        """
        Converts a GraphQL name to python in the same way as SGQLC codegen.
        """
        # This code copied from SGQLC codegen
        s = []
        for w in FieldsManager.re_camel_case_words.findall(name):
            s.append(w.lower())
        name = '_'.join(s)
        if keyword.iskeyword(name):
            return name + '_'
        return name
