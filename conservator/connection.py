from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from conservator.generated.schema import schema

__all__ = [
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
    "ConservatorMalformedQueryException",
]


class ConservatorMalformedQueryException(Exception):
    pass


class ConservatorGraphQLServerError(Exception):
    def __init__(self, message, operation, errors):
        self.message = message
        self.operation = operation
        self.errors = errors


class ConservatorConnection:
    def __init__(self, config):
        self.config = config
        self.graphql_url = ConservatorConnection.to_graphql_url(config.url)
        headers = {
            "authorization": config.key,
        }
        self.endpoint = HTTPEndpoint(self.graphql_url, base_headers=headers)

    @staticmethod
    def to_graphql_url(url):
        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith("graphql"):
            url = url + "/graphql"
        return url

    def run(self, operation, variables=None):
        # TODO remove after flirconservator PR #1988
        if variables is None:
            variables = {}

        json_response = self.endpoint(operation, variables)
        if 'errors' in json_response:
            raise ConservatorGraphQLServerError("Encountered Conservator GraphQL Error on Operation",
                                                operation, json_response['errors'])

        response = (operation + json_response)

        return response

    def query(self, query, operation_base=schema.query_type, include_fields=(), exclude_fields=(), **kwargs):
        op = Operation(operation_base)
        query_name = query.name
        query = getattr(op, query_name)
        query(**kwargs)

        def recursive_add_fields(obj, path=""):
            field_names = [name for name in dir(obj) if not name.startswith("_")]
            if len(field_names) == 0:
                obj()
                return

            for field_name in field_names:
                field = getattr(obj, field_name)
                prefix = ("" if path == "" else path + ".")
                cur_path = prefix + field_name
                # a field is included it's path is in include_fields
                # or it is more specific than something in include_fields
                for included in include_fields:
                    if (cur_path.startswith(included) or included.startswith(cur_path))\
                            and cur_path not in exclude_fields:
                        # unless it is excluded
                        recursive_add_fields(field, cur_path)
                        break

        recursive_add_fields(query)

        return getattr(self.run(op), query_name)

