from FLIR.conservator.generated.schema import Mutation
from FLIR.conservator.wrappers.collection import RemotePathExistsException
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.generated import schema


class Project(QueryableType):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects

    @classmethod
    def create(cls, conservator, name, fields=None):
        """
        Creates a new project with the given `name`, and returns it with the
        specified `fields`.

        Note that this requires the privilege to create projects.
        """
        if len(conservator.projects.by_exact_name(name)) > 0:
            raise RemotePathExistsException(f"A project already exists named '{name}'")
        return conservator.query(Mutation.create_project, name=name, fields=fields)

    def delete(self):
        """
        Delete the project.
        """
        return self._conservator.query(Mutation.delete_project, id=self.id, fields="id")
