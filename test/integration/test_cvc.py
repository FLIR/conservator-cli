"""
This tests the *actual* cvc CLI, no faking it with LocalDataset.

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import os
import subprocess
from time import sleep


def cvc(*args):
    return subprocess.run(
        ["cvc", *map(str, args)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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
    sleep(2)  # It takes a bit for the commit to be saved?

    latest_commit = dataset.get_commit_by_id("HEAD")
    assert latest_commit.short_message == "My test commit"

    # Load new values
    dataset.populate()
    assert dataset.frame_count == 1

    dataset_frames = list(dataset.get_frames())
    assert len(dataset_frames) == 1

    uploaded_frame = dataset_frames[0]
    # Width, height from file
    assert uploaded_frame.width == 500
    assert uploaded_frame.height == 375


def test_cvc_clone_download(default_conservator, tmp_cwd, test_data):
    dataset = default_conservator.datasets.create("My dataset")
    media_id = default_conservator.media.upload(test_data / "mp4" / "adas_thermal.mp4")
    default_conservator.media.wait_for_processing(media_id)
    video = default_conservator.get_media_instance_from_id(media_id)
    video.populate("frames")
    dataset.add_frames(video.frames)
    dataset.commit("Add video frames to dataset")
    sleep(2)

    cvc("clone", dataset.id)
    os.chdir("My dataset")

    p = cvc("download")
    assert p.returncode == 0

    assert os.path.exists("data")
    assert os.path.isdir("data")
    files = os.listdir("data")
    assert len(files) == len(video.frames)


