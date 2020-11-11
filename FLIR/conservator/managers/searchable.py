from FLIR.conservator.managers.type_manager import TypeManager
from FLIR.conservator.paginated_query import PaginatedQuery


class SearchableTypeManager(TypeManager):
    """
    Adds the ability to search using Conservator's Advanced Search.

    The underlying instance must specify a ``search_query``.
    """
    def search(self, search_text):
        """
        Performs a search with the specified `search_text`.
        """
        return PaginatedQuery(self._conservator,
                              self._underlying_type.search_query,
                              search_text=search_text)

