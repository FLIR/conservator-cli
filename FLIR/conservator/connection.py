import re
import urllib.parse

from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from FLIR.conservator.fields_manager import FieldsManager
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import schema

__all__ = [
    "ConservatorMalformedQueryException",
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]


class ConservatorMalformedQueryException(Exception):
    """
    There was a problem with a GraphQL query, and it's the client's
    fault.
    """
    pass


class ConservatorGraphQLServerError(Exception):
    """
    There was a problem with a GraphQL query, and it's unclear
    what the cause was.

    :param operation: The SGQLC operation that caused the error.
    :param errors: A list of errors returned by the server.
    """
    def __init__(self, operation, errors):
        self.operation = operation
        self.errors = errors


class ConservatorConnection:
    """
    Acts as an intermediary between SGQLC and a remote Conservator instance.

    :param config: :class:`~FLIR.conservator.config.Config` providing Conservator URL and user
        authentication info.
    """
    def __init__(self, config):
        self.config = config
        self.graphql_url = ConservatorConnection.to_graphql_url(config.url)
        headers = {
            "authorization": config.key,
        }
        self.endpoint = HTTPEndpoint(self.graphql_url, base_headers=headers)
        self.fields_manager = FieldsManager()

    def get_url_encoded_user(self):
        """
        Returns the encoded email-key combination used to authenticate
        URLs.
        """
        email = urllib.parse.quote(self.config.email.lower(), safe='.')
        key = self.config.key
        return f"{email}:{key}"

    def get_url(self):
        """Returns the base URL for Conservator."""
        r = urllib.parse.urlparse(self.config.url)
        return f"{r.scheme}://{r.netloc}"

    def get_collection_url(self, collection):
        """
        Returns a URL for viewing `collection`.
        """
        return self.get_url() + f"/projects/{collection.id}"

    def get_domain(self):
        """Returns the domain name of the Conservator instance."""
        return urllib.parse.urlparse(self.config.url).netloc

    def get_authenticated_url(self):
        """Returns an authenticated URL that contains an encoded username and token.

        This URL is used when downloading files and repositories."""
        r = urllib.parse.urlparse(self.config.url)
        return f"{r.scheme}://{self.get_url_encoded_user()}@{r.netloc}"

    @staticmethod
    def to_graphql_url(url):
        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith("graphql"):
            url = url + "/graphql"
        return url

    def run(self, operation, variables=None):
        """
        Runs an SGQLC operation on the remote instance, and returns
        the response, if there were no errors.

        If any errors are encountered, they will be raised with a
        :class:`ConservatorGraphQLServerError`.
        """
        # TODO: Remove after flirconservator PR #1988 in prod
        if variables is None:
            variables = {}

        gql = operation.__to_graphql__(auto_select_depth=1)
        gql = re.sub(r'\w* {\s*}\s*', '', gql)
        json_response = self.endpoint(gql, variables)
        errors = json_response.get("errors", None)
        if errors is not None:
            raise ConservatorGraphQLServerError(gql, errors)

        response = (operation + json_response)

        return response

    def _handle_errors(self, errors, type_=None):
        for error in errors:
            if type_ is not None and "Cannot return null for non-nullable field" in error["message"]:
                graphql_fields = tuple(filter(lambda i: isinstance(i, str), error["path"]))
                problematic_path = ".".join(map(FieldsManager.graphql_to_python, graphql_fields[1:]))
                self.fields_manager.add_problematic_path(type_, problematic_path)
                print("Server encountered an error due to a null value for a non-nullable field.")
                print("Attempting to resolve by excluding field in future queries.")
                print("Excluded field:", problematic_path)
                continue

            # we can't handle the errors. raise the exception.
            raise

    def query(self, query, operation_base=None, fields=None, **kwargs):
        """
        Provides an alternative way to prepare and run SGQLC operations.

        :param query: The SGQLC query to run.
        :param operation_base: The base object of the query.
            Defaults to :class:`FLIR.conservator.generated.schema.Query`.
        :param fields: A :class:`FLIR.conservator.fields_request.FieldsRequest` of
            the fields to include (or exclude) in the results.
        :param kwargs: These named parameters are passed as arguments to the query.
        """
        if operation_base is None:
            operation_base = schema.query_type

        if fields is None:
            # includes all fields by default
            fields = FieldsRequest()
        if isinstance(fields, str):
            fields = FieldsRequest(include_fields=(fields,))
        if isinstance(fields, list) or isinstance(fields, tuple):
            fields = FieldsRequest(include_fields=tuple(*fields))

        while True:
            try:
                return self._query(query, operation_base, fields, **kwargs)
            except ConservatorGraphQLServerError as e:
                self._handle_errors(e.errors, query.type)

    def _query(self, query, operation_base, fields, **kwargs):
        type_ = query.type
        op = Operation(operation_base)
        query_name = query.name
        query = getattr(op, query_name)
        query(**kwargs)

        fields.exclude_fields(self.fields_manager.get_problematic_paths(type_))
        fields.add_fields_to_request(query)

        ret = getattr(self.run(op), query_name)
        try:
            if len(ret) == 0:
                # no fields were initialized, meaning the value was likely not found
                return None
        except TypeError:
            # this is thrown if the returned type was a primitive without __len__
            # for instance, a bool or int
            pass

        return ret
