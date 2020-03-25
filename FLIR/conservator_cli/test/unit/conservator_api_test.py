import os

from FLIR.conservator_cli.lib.graphql_api import get_datasets_from_search
from FLIR.conservator_cli.lib.graphql_api import get_collection_by_path
from FLIR.conservator_cli.lib.graphql_api import get_dataset_by_id
from FLIR.conservator_cli.lib.graphql_api import get_history

def get_datasets_from_search_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    assert len(datasets) > 0
    assert datasets[0]["id"]
    assert datasets[0]["name"]
    assert datasets[0]["repository"]
    assert datasets[0]["repository"]["master"]

def get_dataset_by_id_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    dataset = get_dataset_by_id(datasets[0]["id"], access_token)
    assert dataset["id"]
    assert dataset["name"]
    assert dataset["repository"]
    assert dataset["repository"]["master"]

def get_history_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    history = get_history(datasets[0]["repository"]["master"], access_token)
    assert len(history) > 0

def get_collection_by_path_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    collection = get_collection_by_path("/integration-test", access_token)
    assert collection["id"] == "LwWYEXHEGKTCRCc8C"
