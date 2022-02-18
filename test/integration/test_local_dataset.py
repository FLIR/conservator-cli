"""
Test LocalDataset.
"""

import json
import os.path
import pathlib
import shutil
import time

from FLIR.conservator.local_dataset import LocalDataset


def test_clone(conservator, tmp_cwd):
    dataset = conservator.datasets.create("My Dataset")
    local_dset = LocalDataset.clone(dataset)
    assert os.path.exists("My Dataset")
    assert os.path.exists("My Dataset/index.json")
    assert os.path.exists("My Dataset/dataset.jsonl")


def test_add_commit_push_frame(conservator, tmp_cwd, test_data):
    local_path = test_data / "jpg" / "banana_0.jpg"

    dataset = conservator.datasets.create("My Dataset")
    local_dset = LocalDataset.clone(dataset)
    local_dset.stage_local_images([local_path])
    staged_paths = [pathlib.Path(path) for path in local_dset.get_staged_images()]
    assert local_path in staged_paths and len(staged_paths) == 1

    local_dset.push_staged_images()
    assert os.path.exists(local_dset.frames_path)
    frames = local_dset.get_frames()
    assert len(frames) == 1
    assert len(local_dset.get_staged_images()) == 0

    local_dset.add_local_changes()
    status = local_dset.git_status()
    assert os.path.basename(local_dset.frames_path) in status["added"]["staged"]

    local_dset.commit("Test commit", verbose=False)
    status = local_dset.git_status()
    for category in ("added", "modified"):
        for section in ("staged", "working"):
            assert not status[category][section]
    assert not status["other"]

    local_dset.push_commits(verbose=False)

    max_tries = 10
    while not os.path.exists(local_dset.frames_path):
        local_dset.pull(verbose=False)
        time.sleep(1)
        max_tries -= 1
        if max_tries <= 0:
            break
    assert os.path.exists(local_dset.frames_path)
