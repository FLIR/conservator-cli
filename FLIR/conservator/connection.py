import re
import urllib.parse
import logging
import platform
import sys

import requests
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from FLIR.conservator.fields_manager import FieldsManager
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import schema, Query
from FLIR.conservator.version import version as cli_ver
from FLIR.conservator.util import compare_conservator_cli_version

__all__ = [
    "ConservatorMalformedQueryException",
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]

from FLIR.conservator.wrappers import TypeProxy

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
        compare_conservator_cli_version()

        self.config = config
        self.email = None
        self.graphql_url = ConservatorConnection.to_graphql_url(config.url)

        python_ver = sys.version.split()[0]
        os_name = platform.system()
        os_ver = platform.release()
        agent_string = (
            f"conservator-cli/{cli_ver} Python/{python_ver} {os_name}/{os_ver}"
        )
        headers = {
            "authorization": config.key,
            "User-Agent": agent_string,
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

    def query(self, query, operation_base=None, fields=None, **kwargs):
        """
        Provides an alternative way to prepare and run SGQLC operations.

        :param query: The SGQLC query to run.
        :param operation_base: Not required. Included for backwards-compatibility.
        :param fields: A :class:`FLIR.conservator.fields_request.FieldsRequest` of
            the fields to include (or exclude) in the results.
        :param kwargs: These named parameters are passed as arguments to the query.
        """

        tries = 0

        while True:
            try:
                return self._query(query, fields, **kwargs)
            except ConservatorGraphQLServerError as e:
                exception = e.errors[0].get("exception", None)
                if exception is None:
                    # This is a graphql error sent by the server.
                    # The query shouldn't be retried.
                    raise

                # Otherwise we had an error due to connection. We should retry.
                # (see _log_http_error in sgqlc/endpoint/http.py)
                tries += 1
                if tries > self.config.max_retries:
                    raise
                logger.warning("Retrying request after exception: " + str(e))
                logger.warning("Retry #" + str(tries))

    def _query(self, query, fields, **kwargs):
        type_ = query.type
        op = Operation(query.container)
        query_name = query.name
        query = getattr(op, query_name)
        query(**kwargs)

        fr = FieldsRequest.create(fields)
        fr.prepare_query(query)

        result = self.run(op)
        value = getattr(result, query_name)

        return TypeProxy.wrap(self, type_, value)
