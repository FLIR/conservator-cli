import json
import pytest
import time

from FLIR.conservator.generated.schema import AddAssociatedFrameInput


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


def test_add_get_frames_reversed(conservator, test_data):
    local_path1 = test_data / "png" / "flight_0.png"
    local_path2 = test_data / "png" / "flight_1.png"
    media_ids = [conservator.media.upload(local_path1)]
    media_ids.append(conservator.media.upload(local_path2))
    for media_id in media_ids:
        conservator.media.wait_for_processing(media_id)
    images = list(conservator.images.all())
    frames = [image.get_frame() for image in images]

    dataset = conservator.datasets.create("Test dataset")
    dataset.add_frames(frames)

    dataset.populate("frame_count")
    assert dataset.frame_count == 2

    dataset_frames = list(dataset.get_frames())
    assert len(dataset_frames) == 2
    reversed_frames = list(dataset.get_frames_reversed(fields=["dataset_frames.id"]))
    assert len(reversed_frames) == 2

    frame_ids = [frm.id for frm in dataset_frames]
    compare_frame_ids = [frm.id for frm in reversed(reversed_frames)]
    assert compare_frame_ids == frame_ids


def test_associate_frames(conservator, test_data):
    local_path1 = test_data / "png" / "flight_0.png"
    local_path2 = test_data / "png" / "flight_1.png"
    media_ids = [conservator.media.upload(local_path1)]
    media_ids.append(conservator.media.upload(local_path2))
    for media_id in media_ids:
        conservator.media.wait_for_processing(media_id)
    images = list(conservator.images.all())
    frames = [image.get_frame() for image in images]

    dataset1 = conservator.datasets.create("Test dataset1")
    dataset1.add_frames([frames[0]])
    dataset2 = conservator.datasets.create("Test dataset2")
    dataset2.add_frames([frames[1]])

    dset1_frames = list(dataset1.get_frames(fields="dataset_frames.id"))
    dset2_frames = list(dataset2.get_frames(fields="dataset_frames.id"))

    associate_frame_input = AddAssociatedFrameInput(
        dataset_frame_id=dset2_frames[0].id, spectrum="Thermal"
    )
    dataset1.associate_frame(dset1_frames[0].id, associate_frame_input)

    dataset_frames = list(
        dataset1.get_frames(
            fields=["dataset_frames.id", "dataset_frames.associated_frames"]
        )
    )
    assert len(dataset_frames) == 1
    assert len(dataset_frames[0].associated_frames) == 1
    assert dataset_frames[0].associated_frames[0].spectrum == "Thermal"


def test_add_with_associated_frames(conservator, test_data):
    local_path1 = test_data / "png" / "flight_0.png"
    local_path2 = test_data / "png" / "flight_1.png"
    media_ids = [conservator.media.upload(local_path1)]
    media_ids.append(conservator.media.upload(local_path2))
    for media_id in media_ids:
        conservator.media.wait_for_processing(media_id)
    images = list(conservator.images.all())
    frames = [image.get_frame() for image in images]

    dataset = conservator.datasets.create("Test dataset")

    associate_frame_input = AddAssociatedFrameInput(
        frame_id=frames[1].id, spectrum="Thermal"
    )
    association_table = {frames[0].id: [associate_frame_input]}
    dataset.add_frames_with_associations([frames[0]], association_table)

    dataset_frames = list(
        dataset.get_frames(
            fields=["dataset_frames.id", "dataset_frames.associated_frames"]
        )
    )
    assert len(dataset_frames) == 1
    assert len(dataset_frames[0].associated_frames) == 1
    assert dataset_frames[0].associated_frames[0].spectrum == "Thermal"


def test_commit_and_history(conservator, test_data):
    local_path = test_data / "png" / "flight_0.png"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)
    image = conservator.images.all().first()
    frame = image.get_frame()

    dataset = conservator.datasets.create("Test dataset")
    time.sleep(20)
    dataset.populate("repository")
    assert dataset.repository.master is not None
    # All datasets start with two commits.
    assert len(dataset.get_commit_history()) == 2

    dataset.add_frames([frame])
    dataset.commit("My commit message")
    time.sleep(20)

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
