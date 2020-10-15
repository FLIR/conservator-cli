import requests
import time

__all__ = [
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]

from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation
from sgqlc.types import Variable

from conservator.generated.schema import Query


class ConservatorGraphQLServerError(Exception):
    def __init__(self, message, operation, errors):
        self.message = message
        self.operation = operation
        self.errors = errors


class ConservatorMalformedQueryException(Exception):
    pass


class ConservatorConnection:
    def __init__(self, config):
        self.config = config
        headers = {
            "authorization": config.key,
        }
        url = config.url
        if url.endswith("/"):
            url = config.url[:-1]
        if not url.endswith("graphql"):
            url = url + "/graphql"
        self.graphql_url = url
        self.endpoint = HTTPEndpoint(url, base_headers=headers)

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

    def query(self, field, exclude=(), fields=(), **kwargs):
        op = Operation(Query)
        name = field.name
        query = getattr(op, name)
        query(**kwargs)
        if len(fields) > 0 or len(exclude) > 0:
            query.__fields__(*fields, __exclude__=exclude)
        else:
            query.__fields__()
        return getattr(self.run(op), name)

