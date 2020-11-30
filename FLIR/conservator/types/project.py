from FLIR.conservator.types.collection import Collection
from FLIR.conservator.generated import schema


class Project(Collection):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects
