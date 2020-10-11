from sgqlc.types import BaseItem

from conservator.connection import ConservatorGraphQLServerError
from conservator.generated.schema import Query
from conservator.util import to_python_field_name


class PaginatedResults:
    def __init__(self, collection, page=0, limit=10, **kwargs):
        self.collection = collection
        self.contents = []
        self.page = page
        self.limit = limit
        self.kwargs = kwargs

    def next_page(self):
        results = self.collection.get_page(page=self.page, limit=self.limit, **self.kwargs)
        self.page += 1
        return results

    def __iter__(self):
        for item in self.contents:
            yield item

        while True:
            next_page = self.next_page()
            if len(next_page) == 0:
                break
            for item in next_page:
                self.contents.append(item)
                yield item


class QueryableCollection:
    def __init__(self, conservator, query_type):
        self.conservator = conservator
        self.query_type = query_type

    def all(self):
        return self.search("")

    def get_page(self, page=0, limit=100, **kwargs):
        try:
            return self.conservator.query(self.query_type.collection_query,
                                          exclude=self.query_type.excluded,
                                          page=page, limit=limit, **kwargs)
        except ConservatorGraphQLServerError as e:
            for error in e.errors:
                if "Cannot return null for non-nullable field" in error["message"]:
                    problematic_field = error["path"][2]
                    name = to_python_field_name(self.query_type.qtype, problematic_field)
                    if name not in self.query_type.excluded:
                        print("Server encountered an error due to a null value for a non-nullable field.")
                        print("Attempting to resolve by excluding field in future queries.")
                        print("Excluded field:", name)
                        self.query_type.excluded.append(name)
                    continue

                # can't handle this error
                raise
            return self.get_page(page, limit, **kwargs)

    def search(self, search):
        return PaginatedResults(self, search_text=search)





