import os

import pytest as pytest

from FLIR.conservator.generated.schema import AnnotationCreate
from FLIR.conservator.util import md5sum_file


def test_add_annotation(conservator, test_data):
    path = test_data / "jpg" / "bottle_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.images.all().first()
    frame = image.get_frame()

    frame.populate(["annotations", "annotations_count"])
    assert len(frame.annotations) == 0
    assert frame.annotations_count == 0

    annotation_create = AnnotationCreate(
        labels=["bottle", "cat"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    frame.add_annotation(annotation_create)

    frame.populate(["annotations", "annotations_count"])
    assert len(frame.annotations) == 1
    assert frame.annotations_count == 1
    annotation = frame.annotations[0]
    assert annotation.bounding_box.x == 1
    assert annotation.bounding_box.y == 2
    assert annotation.bounding_box.w == 3
    assert annotation.bounding_box.h == 4
    assert annotation.labels == ["bottle", "cat"]
    assert annotation.source.type == "human"


@pytest.mark.skip()
def test_add_prediction(conservator, test_data):
    # There are no classifiers, so this isn't trivial to test.
    # Skipping until someone actually uses it and/or finds a bug.
    pass


def test_download(conservator, test_data, tmp_cwd):
    path = test_data / "jpg" / "bottle_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.images.all().first()
    frame = image.get_frame()

    frame.download(".")
    filename = f"{media_id}-000000.jpg"
    assert os.path.exists(filename)
    assert os.path.isfile(filename)
    assert md5sum_file(filename) == frame.md5
