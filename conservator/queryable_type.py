from sgqlc.types import BaseItem

from conservator.connection import ConservatorGraphQLServerError
from conservator.generated.schema import Query, Project


class QueryableType:
    def __init__(self, qtype, collection_query, count_query, excluded_fields):
        self.qtype = qtype
        self.collection_query = collection_query
        self.count_query = count_query
        self.excluded = excluded_fields


ProjectQueryableType = QueryableType(Project, Query.projects,
                                     Query.projects_query_count,
                                     ["favorite_count", "path", "root_collection"])
