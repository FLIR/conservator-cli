import os
import shutil

from FLIR.conservator_cli.lib.dataset_cache import DatasetCache
from FLIR.conservator_cli.lib.conservator_credentials import ConservatorCredentials

def get_dataset_annotations_test():
    credentials = ConservatorCredentials(os.environ["CONSERVATOR_EMAIL"], os.environ["CONSERVATOR_TOKEN"])
    os.makedirs("tmp", exist_ok=True)
    shutil.rmtree("tmp/dataset_cache", ignore_errors=True)
    os.makedirs("tmp/dataset_cache", exist_ok=True)
    cache = DatasetCache("tmp/dataset_cache", credentials)
    index_path = cache.get_index_filepath("mini-integration-dataset", "478d77e5865382225867a84dd47f813259c05d96")
    print(os.path.relpath(index_path))
    assert os.path.relpath(index_path) == "tmp/dataset_cache/.annotations/mini-integration-dataset/478d77e5865382225867a84dd47f813259c05d96/index.json"

def get_dataset_data_tests():
    credentials = ConservatorCredentials(os.environ["CONSERVATOR_EMAIL"], os.environ["CONSERVATOR_TOKEN"])
    os.makedirs("tmp", exist_ok=True)
    shutil.rmtree("tmp/dataset_cache", ignore_errors=True)
    os.makedirs("tmp/dataset_cache", exist_ok=True)
    cache = DatasetCache("tmp/dataset_cache", credentials)
    folder_path = cache.get_data_folder("mini-integration-dataset", "478d77e5865382225867a84dd47f813259c05d96")
    print(os.path.relpath(folder_path))
    assert os.path.relpath(folder_path) == "tmp/dataset_cache/.data/mini-integration-dataset/478d77e5865382225867a84dd47f813259c05d96/data"
