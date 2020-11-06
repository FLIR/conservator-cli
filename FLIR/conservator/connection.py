import urllib.parse

from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from FLIR.conservator.generated.schema import schema

__all__ = [
    "ConservatorMalformedQueryException",
    "ConservatorGraphQLServerError",
    "ConservatorConnection",
]


class ConservatorMalformedQueryException(Exception):
    pass


class ConservatorGraphQLServerError(Exception):
    def __init__(self, operation, errors):
        self.operation = operation
        self.errors = errors


class ConservatorConnection:
    """
    Acts as an intermediary between SGQLC and a remote Conservator instance.

    :param config: :class:``Config`` providing Conservator URL and user
        authentication info.
    """
    def __init__(self, config):
        self.config = config
        self.graphql_url = ConservatorConnection.to_graphql_url(config.url)
        headers = {
            "authorization": config.key,
        }
        self.endpoint = HTTPEndpoint(self.graphql_url, base_headers=headers)

    def get_git_user(self):
        """
        Returns the encoded email-key combination used to authenticate
        git operations.
        """
        email = urllib.parse.quote(self.config.email.lower(), safe='.')
        key = self.config.key
        return f"{email}:{key}"

    def get_domain(self):
        """Returns the domain name of the Conservator instance."""
        return urllib.parse.urlparse(self.config.url).netloc

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
        :class:``ConservatorGraphQLServerError``.
        """
        # TODO: Remove after flirconservator PR #1988 in prod
        if variables is None:
            variables = {}

        json_response = self.endpoint(operation, variables)
        if 'errors' in json_response:
            raise ConservatorGraphQLServerError(operation, json_response['errors'])

        response = (operation + json_response)

        return response

    def query(self, query, operation_base=schema.query_type, include_fields=(), exclude_fields=(), **kwargs):
        """
        Provides an alternative way to prepare and run SGQLC operations.

        :param query: The SGQLC query to run.
        :param operation_base: The base object of the query.
            Defaults to :class:``FLIR.conservator.generated.schema.Query``.
        :param include_fields: List of field paths to include in the returned object(s).
            Fields of subtypes can be specified as a path separated by ``.``.  For instance,
            when querying for a Dataset, you could add ``repository.master`` to only
            include the ``master`` field of ``Dataset.repository``.
            If empty or not specified, all fields will be included.
        :param exclude_fields: A list of field paths to exclude. These take the same form as
            included fields, and override them. In the above example, excluding ``repository``
            will exclude all fields of ``repository``.
        :param kwargs: These named parameters are passed as arguments to the query.
        """
        op = Operation(operation_base)
        query_name = query.name
        query = getattr(op, query_name)
        query(**kwargs)

        exclude_fields = tuple(set(exclude_fields))
        include_fields = tuple(filter(lambda f: f not in exclude_fields, set(include_fields)))

        max_depth = max(map(lambda f: f.count("."), include_fields + exclude_fields)) + 1

        # Fields are included in a query by calling them.
        # View the SGQLC docs for more info.
        def recursive_add_fields(obj, path="", depth=0):
            field_names = [name for name in dir(obj) if not name.startswith("_")]
            if len(field_names) == 0 or depth >= max_depth:
                obj()
                return

            for field_name in field_names:
                field = getattr(obj, field_name)
                prefix = ("" if path == "" else path + ".")
                cur_path = prefix + field_name
                # A field is included if its path is in include_fields
                # or it is more specific than something in include_fields.
                for included in include_fields:
                    # Unless it is excluded.
                    if (cur_path.startswith(included) or included.startswith(cur_path))\
                            and cur_path not in exclude_fields:
                        recursive_add_fields(field, cur_path, depth + 1)
                        break

        recursive_add_fields(query)

        return getattr(self.run(op), query_name)
