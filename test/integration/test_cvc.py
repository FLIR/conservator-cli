"""
This tests the *actual* cvc CLI, no faking it with LocalDataset.

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import os
import subprocess


def cvc(*args):
    return subprocess.run(["cvc", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_empty_clone(default_conservator, tmp_cwd):
    dataset = default_conservator.datasets.create("My dataset")
    assert dataset is not None

    p = cvc("clone", dataset.id)
    assert p.returncode == 0
    assert os.path.exists("My dataset")

    # We can check the right thing was downloaded by comparing the IDs
    cloned_dataset = default_conservator.datasets.from_local_path("My dataset")
    assert cloned_dataset.id == dataset.id

