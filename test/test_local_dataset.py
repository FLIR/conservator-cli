import os

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.local_dataset import LocalDataset

DATASET_ID = "HdeATtFjRbpJ3cB9d"
DATASET_PATH = "lbtest123"


def test_clone():
    conservator = Conservator.default()
    dataset = conservator.datasets.from_id(DATASET_ID)
    cloned_dataset = LocalDataset.clone(dataset)
    assert cloned_dataset is not None
    assert os.path.abspath(DATASET_PATH) == cloned_dataset.path
    assert os.path.exists(DATASET_PATH)
    assert os.path.exists(DATASET_PATH + "/index.json")


def test_from_path():
    assert os.path.exists("lbtest123")
    local_dataset = LocalDataset(Conservator.default(), DATASET_PATH)
    assert local_dataset is not None
