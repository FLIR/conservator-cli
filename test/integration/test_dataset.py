import json
import pytest
import time


def test_create(conservator):
    dataset = conservator.datasets.create("My Dataset")
    assert dataset is not None
    assert dataset.name == "My Dataset"

    fetched_dataset = conservator.datasets.all().first()
    assert fetched_dataset is not None
    assert fetched_dataset.id == dataset.id
    assert fetched_dataset.name == "My Dataset"


def test_create_in_collection(conservator):
    collection = conservator.collections.create_from_remote_path("/My/Collection")
    dataset = conservator.datasets.create("My Dataset", collections=[collection])

    datasets = list(collection.get_datasets())
    assert len(datasets) == 1
    assert datasets[0].id == dataset.id
    assert datasets[0].name == dataset.name


def test_populate(conservator):
    dataset = conservator.datasets.create("My Dataset")

    dataset_from_id = conservator.datasets.from_id(dataset.id)
    dataset_from_id.populate("name")
    assert dataset_from_id.name == dataset.name


def test_delete(conservator):
    dataset = conservator.datasets.create("My dataset")
    assert conservator.datasets.count() == 1

    dataset.delete()
    assert conservator.datasets.count() == 0


def test_generate_metadata(conservator):
    dataset = conservator.datasets.create("My dataset")

    metadata = dataset.generate_metadata()
    # check that we got metadata that can be parsed into JSON
    try:
        json.loads(metadata)
    except Exception as e:
        assert False, "Exception when parsing metadata as JSON"


def test_add_get_frames(conservator, test_data):
    local_path = test_data / "png" / "flight_0.png"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)
    image = conservator.images.all().first()
    frame = image.get_frame()

    dataset = conservator.datasets.create("Test dataset")
    dataset.add_frames([frame])

    dataset.populate("frame_count")
    assert dataset.frame_count == 1

    dataset_frames = list(dataset.get_frames())
    assert len(dataset_frames) == 1
    assert dataset_frames[0].frame_id == frame.id


def test_commit_and_history(conservator, test_data):
    local_path = test_data / "png" / "flight_0.png"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)
    image = conservator.images.all().first()
    frame = image.get_frame()

    dataset = conservator.datasets.create("Test dataset")
    time.sleep(15)
    dataset.populate("repository")
    assert dataset.repository.master is not None
    # All datasets start with two commits.
    assert len(dataset.get_commit_history()) == 2

    dataset.add_frames([frame])
    dataset.commit("My commit message")
    time.sleep(3)

    commits = dataset.get_commit_history()
    assert len(commits) == 3
    assert commits[0].short_message == "My commit message"


def test_from_string_id(conservator):
    dataset = conservator.datasets.create("My Dataset")

    dataset_from_string = conservator.datasets.from_string(dataset.id, fields=None)
    assert dataset_from_string.id == dataset.id
    assert dataset_from_string.name == dataset.name


def test_from_string_name(conservator):
    dataset = conservator.datasets.create("My Dataset")

    dataset_from_string = conservator.datasets.from_string("My Dataset", fields=None)
    assert dataset_from_string.id == dataset.id
    assert dataset_from_string.name == dataset.name


def test_from_string_path(conservator):
    collection = conservator.collections.create_from_remote_path("/My/Collection")
    dataset = conservator.datasets.create("My Dataset", collections=[collection])

    dataset_from_string = conservator.datasets.from_string(
        "/My/Collection/My Dataset", fields=None
    )
    assert dataset_from_string.id == dataset.id
    assert dataset_from_string.name == dataset.name
