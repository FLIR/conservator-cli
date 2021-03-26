"""
This tests the *actual* cvc CLI, no faking it with LocalDataset.

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import os
import subprocess
import time


def cvc(*args):
    return subprocess.run(
        ["cvc", *map(str, args)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def test_empty_clone(default_conservator, tmp_cwd):
    dataset = default_conservator.datasets.create("My dataset")
    assert dataset is not None

    p = cvc("clone", dataset.id)
    assert p.returncode == 0
    assert os.path.exists("My dataset")

    # We can check the right thing was downloaded by comparing the IDs
    cloned_dataset = default_conservator.datasets.from_local_path("My dataset")
    assert cloned_dataset.id == dataset.id


def test_publish_image(default_conservator, tmp_cwd, test_data):
    dataset = default_conservator.datasets.create("My dataset")
    assert dataset is not None

    p = cvc("clone", dataset.id)
    assert p.returncode == 0
    assert os.path.exists("My dataset")
    os.chdir("My dataset")

    p = cvc("add", test_data / "jpg" / "cat_0.jpg")
    assert p.returncode == 0
    p = cvc("publish", "My test commit")
    assert p.returncode == 0

    time.sleep(2)  # It takes a bit for the commit to be saved?
    latest_commit = dataset.get_commit_by_id("HEAD")
    assert latest_commit.short_message == "My test commit"
