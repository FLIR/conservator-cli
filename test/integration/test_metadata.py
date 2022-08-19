import os
import json
from time import sleep

import pytest

from conftest import wait_for_dataset_commit
from FLIR.conservator.generated.schema import AnnotationCreate

# Unfortunately, metadata references specific IDs, so
# can't be hard-coded test data. Also, can't use a class
# and split download/upload because file system is wiped
# between tests.


@pytest.mark.usefixtures("tmp_cwd")
def test_metadata_download_upload_for_media(conservator, test_data):
    local_path = test_data / "jpg" / "bicycle_0.jpg"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.all().first()
    frame = image.get_frame()
    annotation = AnnotationCreate(
        labels=["abc", "def"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    frame.add_annotations([annotation])

    # First download
    image.download_metadata(".")

    assert os.path.exists("bicycle_0.json")
    assert os.path.isfile("bicycle_0.json")
    with open("bicycle_0.json") as f:
        local_metadata = json.load(f)
    assert local_metadata == json.loads(image.metadata)

    # Double-check format
    assert "videos" in local_metadata
    videos = local_metadata["videos"]
    assert len(videos) == 1
    video = videos[0]
    assert "frames" in video
    frames = video["frames"]
    assert len(frames) == 1
    frame = frames[0]
    assert "annotations" in frame
    annotations = frame["annotations"]
    assert len(annotations) == 1
    annotation = annotations[0]

    # Then, we modify local metadata
    annotations.append(annotation)
    with open("new_metadata.json", "w") as f:
        json.dump(local_metadata, f)

    # Lastly, upload previous metadata and check it matches.
    image.upload_metadata("new_metadata.json")
    sleep(5)  # wait for annotations to be processed
    image.populate("metadata")
    assert local_metadata == json.loads(image.metadata)
    assert len(image.get_annotations()) == 2


# TODO: This test will fail because the import-dataset-metadata worker is not running in k8s.
@pytest.mark.skip()
@pytest.mark.usefixtures("tmp_cwd")
def test_metadata_download_upload_for_dataset(conservator, test_data):
    dataset = conservator.datasets.create("The Dataset")
    assert wait_for_dataset_commit(conservator, dataset.id)
    local_path = test_data / "jpg" / "bicycle_0.jpg"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.all().first()
    frame = image.get_frame()
    annotation = AnnotationCreate(
        labels=["abc", "def"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    frame.add_annotation(annotation)

    dataset.add_frames([frame])

    dataset.download_metadata(".")

    assert os.path.exists("The Dataset.json")
    assert os.path.isfile("The Dataset.json")
    with open("The Dataset.json") as f:
        local_metadata = json.load(f)
    assert local_metadata == json.loads(dataset.generate_metadata())

    # Double-check format
    assert "frames" in local_metadata
    frames = local_metadata["frames"]
    assert len(frames) == 1
    frame = frames[0]
    assert "annotations" in frame
    annotations = frame["annotations"]
    assert len(annotations) == 1
    annotation = annotations[0]

    # Then, we modify local metadata
    annotations.append(annotation)
    with open("new_metadata.json", "w") as f:
        json.dump(local_metadata, f)

    # Lastly, upload previous metadata and check it matches.
    dataset.upload_metadata("new_metadata.json")
    sleep(5)  # wait for annotations to be processed
    new_metadata = dataset.generate_metadata()
    assert local_metadata == json.loads(new_metadata)
    assert len(new_metadata["frames"][0]["annotations"]) == 2
