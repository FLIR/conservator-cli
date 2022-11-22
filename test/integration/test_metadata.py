# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
import os
import json
from time import sleep

import pytest

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
        labels=["abc"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    frame.add_annotations([annotation])

    # First download
    image.download_metadata(".")

    assert os.path.exists("bicycle_0.json")
    assert os.path.isfile("bicycle_0.json")
    with open("bicycle_0.json", encoding="UTF-8") as metadata_file:
        local_metadata = json.load(metadata_file)
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
    with open("new_metadata.json", "w", encoding="UTF-8") as metadata_file:
        json.dump(local_metadata, metadata_file)

    # Lastly, upload previous metadata and check it matches.
    image.upload_metadata("new_metadata.json")
    sleep(5)  # wait for annotations to be processed
    image.populate("metadata")
    assert local_metadata == json.loads(image.metadata)
    assert len(image.get_annotations()) == 2


@pytest.mark.usefixtures("tmp_cwd")
def test_metadata_download_upload_for_dataset(conservator, test_data):
    dataset = conservator.datasets.create("The Dataset")
    assert dataset.wait_for_dataset_commit()
    local_path = test_data / "jpg" / "bicycle_0.jpg"
    media_id = conservator.media.upload(local_path)
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.all().first()
    frame = image.get_frame()
    annotation = AnnotationCreate(
        labels=["abc"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    frame.add_annotations([annotation])

    dataset.add_frames([frame])

    dataset.download_metadata(".")

    assert os.path.exists("The Dataset.json")
    assert os.path.isfile("The Dataset.json")
    with open("The Dataset.json", encoding="UTF-8") as metadata_file:
        local_metadata = json.load(metadata_file)

    # Double-check format
    assert "frames" in local_metadata
    frames = local_metadata["frames"]
    assert len(frames) == 1
    frame = frames[0]
    assert "annotations" in frame
    annotations = frame["annotations"]
    assert len(annotations) == 1
    annotation = annotations[0]
    del annotation["id"]

    # Then, we modify local metadata
    annotations.append(annotation)
    with open("new_metadata.json", "w", encoding="UTF-8") as metadata_file:
        json.dump(local_metadata, metadata_file)

    # Lastly, upload previous metadata and check it matches.
    dataset.upload_metadata("new_metadata.json")

    dataset.populate(["metadata_processing_state"])
    print(dataset.metadata_processing_state)
    for _ in range(60):
        sleep(1)
        dataset.populate(["metadata_processing_state"])
        print(dataset.metadata_processing_state)
        if dataset.metadata_processing_state == "completed":
            break

    new_metadata = json.loads(dataset.generate_metadata())

    assert len(new_metadata["frames"][0]["annotations"]) == 2
