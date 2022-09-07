import dataclasses
import pathlib
import os
import secrets
import shutil
import subprocess
import socket

import pytest
import pymongo

from FLIR.conservator.config import Config
from FLIR.conservator.conservator import Conservator

ADMIN_ROLE = "Conservator Administrator"

PATH = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.realpath(os.path.join(PATH, "..", "data"))
MP4_FOLDER = os.path.join(DATA_FOLDER, "mp4")


@dataclasses.dataclass
class TestSettings:
    server_deployment: str = ""
    conservator_url: str = ""
    mongo_url: str = ""
    pytest_inside_docker: bool = False


test_settings = TestSettings()


def pytest_addoption(parser):
    parser.addoption(
        "--server-deployment",
        choices=["kind", "minikube"],
        default="kind",
        help="Type of deployment for tested conservator instance",
    )


def pytest_configure(config):

    lfs_is_ok = check_git_lfs()

    if not lfs_is_ok:
        error_msg = """
            git-lfs is not installed, or the repository was not initialized correctly
            Please ensure that git-lfs is installed on your system, and then run `git lfs pull`
            to ensure all binary files are checked out correctly
            """
        pytest.exit(error_msg)

    mongo_dns_is_ok = check_conservator_mongo()

    if not mongo_dns_is_ok:
        error_msg = """
            `conservator-mongo` is not configured as a host.
            Please edit your `/etc/hosts` file to contain the following entry:
            `127.0.0.1        conservator-mongo`
            """
        pytest.exit(error_msg)

    # deployment type of Conservator server comes from command-line parser
    test_settings.server_deployment = config.option.server_deployment

    # pytest runtime context (native host or inside container) comes from environment
    test_settings.pytest_inside_docker = (
        os.environ.get("RUNNING_IN_CLI_TESTING_DOCKER") == "True"
    )

    # if using kubernetes, make sure kubectl commands default to using correct cluster
    if test_settings.server_deployment == "kind":
        (code, out) = subprocess.getstatusoutput(
            "kubectl --insecure-skip-tls-verify config use-context kind-kind"
        )
        if code:
            raise RuntimeError(
                f"Could not select '{test_settings.server_deployment} cluster: {out}"
            )
    elif test_settings.server_deployment == "minikube":
        (code, out) = subprocess.getstatusoutput(
            "kubectl --insecure-skip-tls-verify config use-context minikube"
        )
        if code:
            raise RuntimeError(
                f"Could not select '{test_settings.server_deployment} cluster: {out}"
            )

    # conservator URL depends on both server deployment type and runtime context
    conservator_ip = ""
    conservator_port = 0

    if test_settings.server_deployment == "kind":
        # KInD sets up access to webapp at localhost:8080 of the host system,
        # but that is not available at localhost if pytest is inside a container
        conservator_port = 8080

        if test_settings.pytest_inside_docker:
            # If we are in a container, we connect to host.
            conservator_ip = subprocess.getoutput(
                "ip route list default | sed 's/.*via //; s/ .*//' "
            )
        else:
            # Running on host
            conservator_ip = "localhost"
    elif test_settings.server_deployment == "minikube":
        # minikube sets up access to webapp at $MINIKUBE_IP:80
        # where $MINIKUBE_IP is dynamically allocated IP for the minikube container
        conservator_port = 80
        conservator_ip = subprocess.getoutput("minikube ip")

    test_settings.conservator_url = f"http://{conservator_ip}:{conservator_port}"

    # there will be a kubernetes port-forward for mongo access,
    # so it will be available at localhost
    mongo_ip = "localhost"
    mongo_port = (
        27017  # leave port alone -- must match port in mongo replica set config
    )
    test_settings.mongo_url = f"mongodb://{mongo_ip}:{mongo_port}/"


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


@pytest.fixture(scope="session")
def mongo_client():
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

    yield pymongo.MongoClient(test_settings.mongo_url)

    # clean up port-forward process
    port_forward_proc.terminate()


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
def conservator(empty_db):
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
        CONSERVATOR_API_KEY=api_key, CONSERVATOR_URL=test_settings.conservator_url
    )
    print(
        f"Using key={api_key[0]}***{api_key[-1]}, email={admin_email} url={test_settings.conservator_url}"
    )
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


def check_git_lfs():
    which_result = subprocess.call(["which", "git-lfs"], stdout=subprocess.DEVNULL)

    print(f"which result is: {which_result}")

    if which_result != 0:
        return False

    mp4_file = os.path.join(MP4_FOLDER, "tower_gimbal.mp4")

    result = str(subprocess.check_output(["file", mp4_file]))

    if result.find("ASCII") != -1:
        return False

    return True


def check_conservator_mongo():
    try:
        socket.gethostbyname("conservator-mongo")
    except Exception:
        return False
    return True
