import re
import urllib.parse
import logging

import requests
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from FLIR.conservator.fields_manager import FieldsManager
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import schema, Query

__all__ = [
    "ConservatorMalformedQueryException",
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]


logger = logging.getLogger(__name__)


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

    def __str__(self):
        return f"errors='{self.errors}' operation='{self.operation}'"


class ConservatorConnection:
    """
    Acts as an intermediary between SGQLC and a remote Conservator instance.

    :param config: :class:`~FLIR.conservator.config.Config` providing Conservator URL and user
        authentication info.
    """

    def __init__(self, config):
        self.config = config
        self.email = None
        self.graphql_url = ConservatorConnection.to_graphql_url(config.url)
        headers = {
            "authorization": config.key,
        }
        self.endpoint = HTTPEndpoint(self.graphql_url, base_headers=headers)
        self.fields_manager = FieldsManager()

    def get_email(self):
        """Returns the current User's email"""
        if self.email is None:
            user = self.query(Query.user, fields="email")
            self.email = user.email
        return self.email

    def get_url_encoded_user(self):
        """
        Returns the encoded email-key combination used to authenticate
        URLs.
        """
        email = urllib.parse.quote(self.get_email(), safe=".")
        key = self.config.key
        return f"{email}:{key}"

    def get_url(self):
        """
        Returns the base URL for Conservator.
        """
        r = urllib.parse.urlparse(self.config.url)
        return f"{r.scheme}://{r.netloc}"

    def get_collection_url(self, collection):
        """
        Returns a URL for viewing `collection`.
        """
        return self.get_url() + f"/projects/{collection.id}"

    def get_domain(self):
        """
        Returns the domain name of the Conservator instance.
        """
        return urllib.parse.urlparse(self.config.url).netloc

    def get_authenticated_url(self):
        """
        Returns an authenticated URL that contains an encoded username and token.

        This URL is used when downloading files and repositories.
        """
        r = urllib.parse.urlparse(self.config.url)
        return f"{r.scheme}://{self.get_url_encoded_user()}@{r.netloc}"

    def get_dvc_url(self):
        """
        Returns the DVC URL used for downloading files.
        """
        return f"{self.get_authenticated_url()}/dvc"

    def get_dvc_hash_url(self, md5):
        """
        Returns the DVC URL for downloading content with the given `md5` hash.
        """
        return f"{self.get_dvc_url()}/{md5[:2]}/{md5[2:]}"

    def dvc_hash_exists(self, md5):
        """
        Returns `True` if DVC contains the given `md5` hash, and `False` otherwise.
        """
        hash_url = self.get_dvc_hash_url(md5)
        # We only care about the status code, so we use .head
        r = requests.head(hash_url)
        # 302 means the file was found.
        return r.status_code == 302

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

        # The depth is completely arbitrary atm...
        gql = operation.__to_graphql__(auto_select_depth=5)
        gql = re.sub(r"\w* {\s*}\s*", "", gql)
        json_response = self.endpoint(gql, variables)
        logger.debug("Response: " + str(json_response))
        errors = json_response.get("errors", None)
        if errors is not None:
            raise ConservatorGraphQLServerError(gql, errors)

        response = operation + json_response

        return response

    def _handle_errors(self, errors, type_=None):
        for error in errors:
            if (
                type_ is not None
                and "Cannot return null for non-nullable field" in error["message"]
            ):
                graphql_fields = tuple(
                    filter(lambda i: isinstance(i, str), error["path"])
                )
                problematic_path = ".".join(
                    map(FieldsManager.graphql_to_python, graphql_fields[1:])
                )
                self.fields_manager.add_problematic_path(type_, problematic_path)
                logger.debug(
                    "Server encountered an error due to a null value for a non-nullable field."
                )
                logger.debug(
                    "Attempting to resolve by excluding field in future queries."
                )
                logger.debug(f"Excluded field: {type_.__name__}.{problematic_path}")
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

        tries = 0

        while True:
            # TODO: This retry logic is pretty messy. We should refactor and add tests.
            try:
                try:
                    return self._query(query, operation_base, fields, **kwargs)
                except ConservatorGraphQLServerError as e:
                    self._handle_errors(e.errors, query.type)
            except ConservatorGraphQLServerError as e:
                exception = e.errors[0].get("exception", None)
                if exception is None:
                    # this is a graphql error that couldn't be handled
                    raise
                # otherwise it's an error due to connection
                # (see _log_http_error in sgqlc/endpoint/http.py)
                tries += 1
                if tries > self.config.max_retries:
                    raise
                logger.debug("Retrying request after exception: " + str(exception))
                logger.debug("Retry #" + str(tries))
            except Exception as e:
                tries += 1
                if tries > self.config.max_retries:
                    raise
                logger.debug("Retrying request after exception: " + str(e))
                logger.debug("Retry #" + str(tries))

    def _query(self, query, operation_base, fields, **kwargs):
        type_ = query.type
        op = Operation(operation_base)
        query_name = query.name
        query = getattr(op, query_name)
        query(**kwargs)

        fr = FieldsRequest.create(fields)
        fr.exclude_fields(self.fields_manager.get_problematic_paths(type_))
        fr.prepare_query(query)

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
