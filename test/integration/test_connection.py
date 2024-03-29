# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
import requests


def test_connection(conservator):
    url = conservator.get_url()
    response = requests.get(url, timeout=10)
    assert response.ok


def test_graphql_endpoint(conservator):
    response = requests.get(conservator.graphql_url, timeout=10)
    # Unauthenticated query, this verifies the route exists
    assert response.status_code == 400


def test_authenticated(conservator):
    # Querying current user is also how webapp checks if authenticated
    user = conservator.get_user()
    assert user is not None
