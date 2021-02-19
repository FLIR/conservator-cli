from FLIR.conservator.managers.type_manager import TypeManager
from FLIR.conservator.paginated_query import PaginatedQuery


class SearchableTypeManager(TypeManager):
    """
    Adds the ability to search using Conservator's Advanced Search.

    The underlying type must specify a ``search_query``.

    Most queries return a :class:`FLIR.conservator.paginated_query.PaginatedQuery`.
    """

    def search(self, search_text, **kwargs):
        """
        Performs a search with the specified `search_text`.
        """
        return PaginatedQuery(
            self._conservator,
            query=self._underlying_type.search_query,
            search_text=search_text,
            **kwargs,
        )

    def by_exact_name(self, name, fields=None):
        """
        Returns a search for an exact `name`.

        Convert the returned query to a list, and check length to determine if a
        single match was found (or none, or many).
        """
        return self.search(f'name:"{name}"', fields=fields).filtered_by(name=name)

    def all(self):
        """Searches for all instances"""
        return self.search("")

    def count(self, search_text=""):
        """Returns the number of instances that are returned by `search_text`"""
        return len(self.search(search_text).including_fields("id"))

    def count_all(self):
        """Returns total number of instances"""
        return len(self.search("").including_fields("id"))
