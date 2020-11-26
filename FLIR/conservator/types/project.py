import FLIR.conservator.types as types
from FLIR.conservator.generated import schema


class Project(types.Collection):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects
