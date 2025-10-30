# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
"""
This tests the *actual* cvc CLI, no faking it with LocalDataset.

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import os
import subprocess
from time import sleep
import pytest


def cvc(*args):
    return subprocess.run(
        ["cvc", *map(str, args)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


@pytest.mark.usefixtures("tmp_cwd")
def test_empty_clone(default_conservator):
    dataset = default_conservator.datasets.create("My dataset")
    assert dataset is not None
    assert dataset.wait_for_dataset_commit()

    clone_output = cvc("clone", dataset.id)
    assert clone_output.returncode == 0
    assert os.path.exists("My dataset")

    # We can check the right thing was downloaded by comparing the IDs
    cloned_dataset = default_conservator.datasets.from_local_path("My dataset")
    assert cloned_dataset.id == dataset.id


@pytest.mark.usefixtures("tmp_cwd")
def test_publish_image(default_conservator, test_data):
    dataset = default_conservator.datasets.create("Publish Image Dataset")
    assert dataset is not None
    assert dataset.wait_for_dataset_commit()

    cvc_output = cvc("clone", dataset.id)
    assert cvc_output.returncode == 0
    assert os.path.exists("Publish Image Dataset")
    os.chdir("Publish Image Dataset")

    cvc_output = cvc("stage-image", test_data / "jpg" / "cat_0.jpg")
    assert cvc_output.returncode == 0
    cvc_output = cvc("publish", "publish image test commit")
    assert cvc_output.returncode == 0

    dataset.wait_for_history_len(3, max_tries=100)
    latest_commit = dataset.get_commit_by_id("HEAD")
    assert latest_commit.short_message == "publish image test commit"

    # Load new values
    dataset.populate()
    assert dataset.frame_count == 1

    dataset_frames = list(dataset.get_frames())
    assert len(dataset_frames) == 1

    uploaded_frame = dataset_frames[0]
    # Width, height from file
    assert uploaded_frame.width == 500
    assert uploaded_frame.height == 375


@pytest.mark.usefixtures("tmp_cwd")
def test_cvc_clone_download(default_conservator, test_data):
    dataset = default_conservator.datasets.create("My dataset")
    assert dataset.wait_for_dataset_commit()
    media_id = default_conservator.media.upload(test_data / "mp4" / "adas_thermal.mp4")
    default_conservator.media.wait_for_processing(media_id)
    video = default_conservator.get_media_instance_from_id(media_id)
    frames = video.get_frames()
    dataset.add_frames(frames)
    commit_message = "Add video frames to dataset"
    dataset.commit(commit_message)

    # wait up to 30 sec for commit to appear.
    history = []
    for _ in range(30):
        sleep(1)
        history = dataset.get_commit_history(fields="short_message")
        if history[0].short_message == commit_message:
            break
    assert history
    assert history[0].short_message == commit_message

    cvc("clone", dataset.id)
    os.chdir("My dataset")

    download_output = cvc("download")
    assert download_output.returncode == 0

    assert os.path.exists("data")
    assert os.path.isdir("data")
    files = os.listdir("data")
    assert len(files) == len(frames)
