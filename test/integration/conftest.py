import secrets
import shutil
import subprocess

import pytest
import pymongo

from FLIR.conservator.config import Config
from FLIR.conservator.conservator import Conservator

ADMIN_ROLE = "Conservator Administrator"


@pytest.fixture(scope="session")
def using_kubernetes():
    if shutil.which("kubectl") is None:
        return False
    proc = subprocess.run(
        ["kubectl", "get", "services", "-o", "name"], stdout=subprocess.PIPE, text=True
    )
    if "conservator-webapp" in proc.stdout:
        return True
    return False


def get_mongo_pod_name():
    # When running in k8s, the full name of the pod running mongo
    cmd = subprocess.run(
        ["kubectl", "get", "pods", "-o", "name"], stdout=subprocess.PIPE, text=True
    )
    pod_names = cmd.stdout.splitlines(keepends=False)
    for pod_name in pod_names:
        if "conservator-mongo" in pod_name:
            return pod_name
    raise RuntimeError("Can't find mongo pod")


@pytest.fixture(scope="session")
def mongo_client(using_kubernetes):
    if using_kubernetes:
        mongo_pod_name = get_mongo_pod_name()
        # Port forward 27030 in the background...
        port_forward_proc = subprocess.Popen(
            ["kubectl", "port-forward", mongo_pod_name, f"27030:27017"]
        )
        yield pymongo.MongoClient("mongodb://localhost:27030/")
        port_forward_proc.terminate()
    else:  # Using docker
        mongo_addr_proc = subprocess.run(
            ["docker", "inspect", "conservator_mongo", "-f", "{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}"],
            stdout=subprocess.PIPE,
            text=True
        )
        domain = mongo_addr_proc.stdout.strip()
        port = 27017
        yield pymongo.MongoClient(host=[f"{domain}:{port}"])


@pytest.fixture(scope="session")
def db(mongo_client):
    for name in mongo_client.list_database_names():
        if name.startswith("flir-conservator"):
            return mongo_client.get_database(name)
    raise RuntimeError("Can't find database")


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
    empty_db.users.insert_one(
        {
            "_id": Conservator.generate_id(),
            "role": ADMIN_ROLE,
            "name": "admin user",
            "email": "admin@example.com",
            "apiKey": api_key,
            "organizationId": organization_id,
        }
    )
    config = Config(
        CONSERVATOR_API_KEY=api_key, CONSERVATOR_URL="http://localhost:8080"
    )
    yield Conservator(config)
