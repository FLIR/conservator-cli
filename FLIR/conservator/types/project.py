from FLIR.conservator.types.type_proxy import  TypeProxy
from FLIR.conservator.generated import schema


class Project(TypeProxy):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects
