from FLIR.conservator.managers.type_manager import TypeManager
from FLIR.conservator.paginated_query import PaginatedQuery


class SearchableTypeManager(TypeManager):
    """
    Adds the ability to search using Conservator's Advanced Search.

    The underlying type must specify a ``search_query``.

    Most queries return a :class:`FLIR.conservator.paginated_query.PaginatedQuery`.
    """

    def search(self, search_text):
        """
        Performs a search with the specified `search_text`.
        """
        return PaginatedQuery(
            self._conservator,
            self._underlying_type,
            self._underlying_type.search_query,
            search_text=search_text,
        )

    def all(self):
        """Searches for all instances"""
        return self.search("")

    def count(self, search_text=""):
        """Returns the number of instances that are returned by `search_text`"""
        return len(self.search(search_text).including_fields("id"))

    def count_all(self):
        """Returns total number of instances"""
        return len(self.search("").including_fields("id"))
