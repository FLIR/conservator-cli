import os

import pytest as pytest

from FLIR.conservator.generated.schema import AnnotationCreate, PredictionCreate, Query
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


def test_add_prediction(conservator, test_data):
    path = test_data / "jpg" / "bottle_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.images.all().first()
    frame = image.get_frame()

    frame.populate(["annotations", "machine_annotations_count"])
    assert len(frame.annotations) == 0
    assert frame.machine_annotations_count == 0

    classifiers = conservator.query(Query.classifiers)
    assert len(classifiers) > 0
    classifier_id = classifiers[0].id

    prediction_create = PredictionCreate(
        labels=["boo", "far"],
        bounding_box={"x": 6, "y": 5, "w": 4, "h": 3},
        classifier_id=classifier_id,
    )
    frame.add_prediction(prediction_create)

    frame.populate(["annotations", "machine_annotations_count"])
    assert len(frame.annotations) == 1
    assert frame.machine_annotations_count == 1
    annotation = frame.annotations[0]
    assert annotation.bounding_box.x == 6
    assert annotation.bounding_box.y == 5
    assert annotation.bounding_box.w == 4
    assert annotation.bounding_box.h == 3
    assert annotation.labels == ["boo", "far"]
    assert annotation.source.type == "machine"


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
