import requests
import time

__all__ = [
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]

class ConservatorGraphQLServerError(Exception):
    def __init__(self, status_code, message, server_error):
        self.status_code = status_code
        self.message = message
        self.server_error = server_error


class ConservatorConnection:
    def __init__(self, credentials, url):
        self.credentials = credentials
        self.url = url

    def query(self, query, variables):
        graphql_endpoint = 'https://flirconservator.com/graphql'
        headers = {'Authorization': "{}".format(self.credentials.key)}

        r = requests.post(graphql_endpoint, headers=headers, json={"query": query, "variables": variables})
        response = r.json()

        # response with 'data' but not 'errors' means valid results
        if response.get("errors"):
            raise ConservatorGraphQLServerError(r.status_code, "Server rejected query", r.content)

        if response.get("data"):
            return response["data"]

        raise ConservatorGraphQLServerError(r.status_code, "Invalid server response", r.content)


