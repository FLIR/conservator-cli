from FLIR.conservator.generated.schema import Mutation
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
        return conservator.query(
            Mutation.create_project, operation_base=Mutation, name=name, fields=fields
        )

    def delete(self):
        """
        Delete the project.
        """
        return self._conservator.query(
            Mutation.delete_project, operation_base=Mutation, id=self.id
        )
