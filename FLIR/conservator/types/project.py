from FLIR.conservator.generated.schema import Mutation
from FLIR.conservator.types.type_proxy import  TypeProxy
from FLIR.conservator.generated import schema


class Project(TypeProxy):
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
        result = conservator.query(Mutation.create_project, operation_base=Mutation,
                                   name=name, fields=fields)
        return cls(conservator, result)

    def delete(self):
        """
        Delete the project.
        """
        self._conservator.query(Mutation.delete_project, operation_base=Mutation,
                                id=self.id)
