import os
import json
from time import sleep

import pytest as pytest

from FLIR.conservator.generated.schema import AnnotationCreate

# Unfortunately, metadata references specific IDs, so
# can't be hard-coded test data. Also, can't use a class
# and split download/upload because file system is wiped
# between tests.


def test_metadata_download_upload_for_media(conservator, test_data, tmp_cwd):
    collection = conservator.collections.create_from_remote_path("/Some/Collection")
    local_path = test_data / "jpg" / "bicycle_0.jpg"
    media_id = conservator.media.upload(local_path, collection=collection)
    conservator.media.wait_for_processing(media_id)
    
    image = conservator.images.all().first()
    frame = image.get_frame()
    annotation = AnnotationCreate(labels=["abc", "def"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4})
    frame.add_annotation(annotation)

    # First download
    image.download_metadata(".")

    assert os.path.exists("bicycle_0.json")
    assert os.path.isfile("bicycle_0.json")
    with open("bicycle_0.json") as f:
        local_metadata = json.load(f)
    assert local_metadata == json.loads(image.metadata)

    # Then, we modify local metadata
    annotation = local_metadata["videos"][0]["frames"][0]["annotations"][0]
    local_metadata["videos"][0]["frames"][0]["annotations"].append(annotation)
    with open("new_metadata.json", "w") as f:
        json.dump(local_metadata, f)

    # Lastly, upload previous metadata and check it matches.
    image.upload_metadata("new_metadata.json")
    sleep(5)  # wait for annotations to be processed
    image.populate("metadata")
    assert local_metadata == json.loads(image.metadata)


@pytest.mark.skip()
def test_metadata_download_upload_for_dataset(conservator, test_data, tmp_cwd):
    # TODO: download_metadata does not work on Dataset: no field metadata
    # Can switch to using generateMetadata, or remove.
    pass

