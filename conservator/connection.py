import requests
import time

__all__ = [
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]

from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from conservator.generated.schema import Query
from conservator.util import to_clean_string


class ConservatorGraphQLServerError(Exception):
    def __init__(self, message, operation, errors):
        self.message = message
        self.operation = operation
        self.errors = errors


class ConservatorConnection:
    def __init__(self, credentials, url):
        self.credentials = credentials
        self.url = url
        headers = {
            "authorization": credentials.key,
        }
        self.endpoint = HTTPEndpoint(url, base_headers=headers)

    def run(self, operation, variables=None):
        # TODO remove after flirconservator PR #1988
        if variables is None:
            variables = {}

        json_response = self.endpoint(operation, variables)
        if 'errors' in json_response:
            raise ConservatorGraphQLServerError("Encountered Conservator GraphQL Error on Operation", operation, json_response['errors'])

        response = (operation + json_response)

        return response

    def query(self, field, exclude=(), **kwargs):
        op = Operation(Query)
        name = field.name
        query = getattr(op, name)
        query(**kwargs)
        query.__fields__(__exclude__=exclude)
        return getattr(self.run(op), name)

