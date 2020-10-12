from conservator.type import QueryableType


class PaginatedResults:
    def __init__(self, collection, page_size=100, fields=(), **kwargs):
        self.collection = collection
        self.contents = []
        self.page = 0
        self.limit = page_size
        self.kwargs = kwargs
        self.fields = list(fields)
        self.done = False

    def with_fields(self, *fields):
        for field in fields:
            if field not in self.fields:
                self.fields.append(field)
        return self

    def next_page(self):
        results = self.collection.get_page(fields=self.fields,
                                           page=self.page,
                                           limit=self.limit,
                                           **self.kwargs)
        self.page += 1
        return results

    def __iter__(self):
        for item in self.contents:
            yield item

        while not self.done:
            next_page = self.next_page()
            for item in next_page:
                self.contents.append(item)
                yield item
            if len(next_page) < self.limit:
                self.done = True
                return

    def __len__(self):
        return len(list(self.__iter__()))


class QueryableCollection:
    def __init__(self, conservator, queryable_type):
        self.conservator = conservator
        self.queryable_type = queryable_type

    def all(self):
        return self.search("")

    def get_page(self, page=0, limit=100, **kwargs):
        return self.queryable_type.query(self.conservator, page=page, limit=limit, **kwargs)

    def search(self, search_text):
        return PaginatedResults(self, search_text=search_text)

    def count(self, search_text=""):
        return len(self.search(search_text))

    def get(self, idx, fields=(), all_fields=False):
        if all_fields:
            fields = self.queryable_type.get_all_fields()
        item = self.queryable_type.from_id(self.conservator, idx)
        item.populate(fields)
        return item

