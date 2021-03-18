import datetime
import secrets

import pytest
import pymongo

from FLIR.conservator.config import Config
from FLIR.conservator.conservator import Conservator

ADMIN_ROLE = "Conservator Administrator"


@pytest.fixture()
def db():
    # TODO: Get these from docker inspect.
    domain = "172.17.0.2"
    port = 27017
    database_name = "flir-conservator-development"
    client = pymongo.MongoClient(host=[f"{domain}:{port}"])
    return client.get_database(database_name)


@pytest.fixture()
def empty_db(db):
    PRESERVED_COLLECTIONS = ["groups", "organizations"]
    for name in db.list_collection_names():
        if name.startswith("system."):
            continue
        if name in PRESERVED_COLLECTIONS:
            continue
        db.get_collection(name).delete_many({})
    return db


@pytest.fixture()
def conservator(empty_db):
    """
    Provides a Conservator connection to be used for testing.

    The Conservator's database will be empty except for users and organizations. This
    instance will have admin permissions, integration suites do not (currently) test
    permissions. It's assumed we can do anything.
    """
    # TODO: Initialize an organization, groups.
    organization_id = empty_db.organizations.find_one({})["_id"]
    api_key = secrets.token_urlsafe(16)
    empty_db.users.insert_one({
        "_id": Conservator.generate_id(),
        "role": ADMIN_ROLE,
        "name": "admin user",
        "email": "admin@example.com",
        "apiKey": api_key,
        "organizationId": organization_id,
    })
    config = Config(CONSERVATOR_API_KEY=api_key, CONSERVATOR_URL="http://localhost:3000")
    yield Conservator(config)
