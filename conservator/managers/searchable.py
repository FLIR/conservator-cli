from conservator.managers.type_manager import TypeManager
from conservator.types.searchable import SearchableType


class PaginatedSearchResults:
    def __init__(self, collection, page_size=100, fields=(), **kwargs):
        self.collection = collection
        self.contents = []
        self.page = 0
        self.limit = page_size
        self.kwargs = kwargs
        self.fields = list(fields)
        self.done = False

    def with_fields(self, *fields):
        if len(fields) == 0:
            return self.with_all_fields()
        for field in fields:
            if field not in self.fields:
                self.fields.append(field)
        return self

    def with_all_fields(self):
        self.with_fields(*self.collection.underlying_type.underlying_type.__field_names__)
        return self

    def first(self):
        if len(self.contents) > 0:
            return self.contents[0]
        first = self.collection.get_page(fields=self.fields,
                                         page=0,
                                         limit=1,
                                         **self.kwargs)[0]
        self.contents.append(first)
        return first

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


class SearchableTypeManager(TypeManager):
    def __init__(self, conservator, searchable_type):
        assert issubclass(searchable_type, SearchableType)
        super().__init__(conservator, searchable_type)

    def all(self):
        return self.search("")

    def get_page(self, page=0, limit=100, **kwargs):
        return self.underlying_type.search(self.conservator, page=page, limit=limit, **kwargs)

    def search(self, search_text, **kwargs):
        return PaginatedSearchResults(self, search_text=search_text, **kwargs)

    def count(self, search_text=""):
        return len(self.search(search_text))

    def first(self, **kwargs):
        return self.underlying_type.search(self.conservator, page=0, limit=1, **kwargs)[0]

