import pathlib
import os
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
    kube_services = subprocess.getoutput(
        "kubectl --insecure-skip-tls-verify get services -o name"
    )
    if "conservator-webapp" in kube_services:
        return True
    return False


def get_mongo_pod_name():
    # When running in k8s, the full name of the pod running mongo
    kube_pods = subprocess.getoutput(
        "kubectl --insecure-skip-tls-verify get pods -o name"
    )
    pod_names = kube_pods.splitlines(keepends=False)
    for pod_name in pod_names:
        if "conservator-mongo" in pod_name:
            return pod_name
    raise RuntimeError("Can't find mongo pod")


def running_in_testing_docker():
    # We might be running in test Docker, we have an environment
    # variable set to be able to check. This determines how we
    # connect to docker or k8s.
    return os.environ.get("RUNNING_IN_CLI_TESTING_DOCKER") == "True"


@pytest.fixture(scope="session")
def conservator_domain(using_kubernetes):
    # If we are in a container, we connect to host.
    if running_in_testing_docker():
        host_ip = subprocess.getoutput(
            "ip route list default | sed 's/.*via //; s/ .*//' "
        )
        return host_ip  # Host IP
    # Running on host
    return "localhost"


@pytest.fixture(scope="session")
def mongo_client(using_kubernetes, conservator_domain):
    if using_kubernetes:
        mongo_pod_name = get_mongo_pod_name()
        # Port forward 27017 in the background...
        # note that it should be the standard mongo port,
        # anything else causes problems if mongodb server
        # has been configured with replica set
        port_forward_proc = subprocess.Popen(
            [
                "kubectl",
                "--insecure-skip-tls-verify",
                "port-forward",
                "service/conservator-mongo",
                f"27017:27017",
            ]
        )
        # Because of the port forward process, mongo will be accessible on localhost
        yield pymongo.MongoClient(f"mongodb://localhost:27017/")
        port_forward_proc.terminate()
    else:  # Using docker
        domain = subprocess.getoutput(
            "docker inspect conservator_mongo -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'"
        ).strip()
        yield pymongo.MongoClient(host=[f"{domain}:27017"])


@pytest.fixture(scope="session")
def db(mongo_client):
    for name in mongo_client.list_database_names():
        if name.startswith("flir-conservator"):
            return mongo_client.get_database(name)
    raise RuntimeError("Can't find database")


@pytest.fixture(scope="class")
def empty_db(db):
    PRESERVED_COLLECTIONS = ["groups", "organizations", "allowedDomains"]
    for name in db.list_collection_names():
        if name.startswith("system."):
            continue
        if name in PRESERVED_COLLECTIONS:
            continue
        db.get_collection(name).delete_many({})
    return db


@pytest.fixture(scope="class")
def conservator(empty_db, conservator_domain):
    """
    Provides a Conservator connection to be used for testing.

    The Conservator's database will be empty except for users and organizations. This
    instance will have admin permissions, integration suites do not (currently) test
    permissions. It's assumed we can do anything.
    """
    # TODO: Initialize an organization, groups.
    organization = empty_db.organizations.find_one({})
    assert organization is not None, "Make sure conservator is initialized"
    if "TEST_API_KEY" in os.environ:
        api_key = os.environ["TEST_API_KEY"]
    else:
        api_key = secrets.token_urlsafe(16)
    if "TEST_ADMIN_EMAIL" in os.environ:
        admin_email = os.environ["TEST_ADMIN_EMAIL"]
    else:
        admin_email = "admin@example.com"

    empty_db.users.insert_one(
        {
            "_id": Conservator.generate_id(),
            "role": ADMIN_ROLE,
            "name": "admin user",
            "email": admin_email,
            "apiKey": api_key,
            "organizationId": organization["_id"],
        }
    )
    config = Config(
        CONSERVATOR_API_KEY=api_key, CONSERVATOR_URL=f"http://{conservator_domain}:8080"
    )
    print(f"Using key={api_key}, email={admin_email} url=http://{conservator_domain}:8080")
    yield Conservator(config)


@pytest.fixture(scope="class")
def default_conservator(conservator):
    """
    Set the default config to point to conservator, for use when
    testing CLI commands.
    """
    config = conservator.config
    config.save_to_default_config()
    yield conservator
    config.delete_saved_default_config()


@pytest.fixture()
def tmp_cwd(tmp_path):
    """
    Set the current working directory to a temporary path for the duration
    of the test. Then restore the current working directory and delete the path.
    """
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
    shutil.rmtree(tmp_path)


@pytest.fixture(scope="session")
def root_path():
    # __file__ should be conservator-cli/test/integration/conftest.py
    # up three parents would be conservator-cli/
    root = pathlib.Path(__file__).parent.parent.parent
    return root


@pytest.fixture(scope="session")
def test_data(root_path):
    return root_path / "test" / "data"


def upload_media(conservator, media):
    """
    Utility method for uploading some media to conservator instance.

    `media` takes the form ``[(local_path, remote_path, remote_name), ...]``
    """
    media_ids = []
    for local_path, remote_path, remote_name in media:
        collection = None
        if remote_path is not None:
            collection = conservator.collections.from_remote_path(
                remote_path, make_if_no_exist=True
            )
        media_id = conservator.media.upload(
            local_path, collection=collection, remote_name=remote_name
        )
        media_ids.append(media_id)
    conservator.media.wait_for_processing(media_ids)
