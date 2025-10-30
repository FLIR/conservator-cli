# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
import json
import pytest

from FLIR.conservator.generated.schema import (
    CreateDatasetAnnotationInput,
    UpdateAnnotationInput,
)


class TestDatasetFrame:
    @pytest.fixture(scope="class", autouse=True)
    def init_dataset(self, conservator, test_data):
        local_path = test_data / "png" / "flight_0.png"
        media_id = conservator.media.upload(local_path)
        conservator.media.wait_for_processing(media_id)
        image = conservator.images.all().first()
        frame = image.get_frame()
        dataset = conservator.datasets.create("Test dataset")
        assert dataset.wait_for_dataset_commit()
        dataset.add_frames([frame])

    def test_initial_state(self, conservator):
        # Good to test initial conditions the other tests will assume
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        assert not frame.is_flagged
        assert not frame.is_empty
        assert frame.qa_status is None

    def test_flag(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.flag()

        frame.populate("is_flagged")
        assert frame.is_flagged

    def test_unflag(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unflag()

        frame.populate("is_flagged")
        assert not frame.is_flagged

    def test_mark_empty(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.mark_empty()

        frame.populate("is_empty")
        assert frame.is_empty

    def test_unmark_empty(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unmark_empty()

        frame.populate("is_empty")
        assert not frame.is_empty

    def test_approve(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.approve()

        frame.populate("qa_status")
        assert frame.qa_status == "approved"

    def test_request_changes(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.request_changes()

        frame.populate("qa_status")
        assert frame.qa_status == "changesRequested"

    def test_qa_status_note(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        change_note = "Test QA status note"
        frame.request_changes()
        frame.update_qa_status_note(change_note)

        frame.populate(["qa_status", "qa_status_note"])
        assert frame.qa_status == "changesRequested"
        assert frame.qa_status_note == change_note

    def test_unset_qa_status(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unset_qa_status()

        frame.populate("qa_status")
        assert frame.qa_status is None

    def test_add_dataset_annotations(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        annotation_create = CreateDatasetAnnotationInput(
            labels=["bottle"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
        )

        dataset_frame.add_dataset_annotations([annotation_create])

        fields = [
            "annotations.id",
            "annotations.labels",
            "annotations.bounding_box.x",
            "annotations.bounding_box.y",
            "annotations.bounding_box.w",
            "annotations.bounding_box.h",
        ]

        dataset_frame.populate(fields)

        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]

        assert annotation.id is not None

        assert annotation.labels is not None
        assert annotation.labels[0] == "bottle"

        assert annotation.bounding_box is not None
        assert annotation.bounding_box.x == 1
        assert annotation.bounding_box.y == 2
        assert annotation.bounding_box.w == 3
        assert annotation.bounding_box.h == 4

    def test_set_dataset_annotation_metadata(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        dataset_frame.populate("annotations.id")

        if len(dataset_frame.annotations) == 0:
            annotation_create = CreateDatasetAnnotationInput(
                labels=["bottle"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
            )

            dataset_frame.add_dataset_annotations([annotation_create])

            dataset_frame.populate("annotations.id")

        assert len(dataset_frame.annotations) == 1

        assert dataset_frame.annotations[0].id is not None

        annotation_id = dataset_frame.annotations[0].id

        annotation_metadata = {
            "metadata": True,
            "custom": "metadata",
        }

        dataset_frame.set_dataset_annotation_metadata(
            annotation_id=annotation_id,
            annotation_metadata=json.dumps(annotation_metadata),
        )

        dataset_frame.populate("annotations.custom_metadata")

        created_metadata = dataset_frame.annotations[0].custom_metadata

        assert created_metadata is not None
        assert json.loads(created_metadata) == annotation_metadata

    def test_update_dataset_annotations(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        fields = ["annotations.id", "annotations.labels"]

        dataset_frame.populate(fields)

        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]
        assert annotation.labels == ["bottle"]
        annotation_update = UpdateAnnotationInput(labels=["person"])
        dataset_frame.update_dataset_annotation(annotation_update, annotation.id)
        dataset_frame.populate(fields)

        annotation = dataset_frame.annotations[0]
        assert annotation.labels == ["person"]

    def test_approve_dataset_annotation(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        fields = ["annotations.id", "annotations.labels", "annotations.qa_status"]

        dataset_frame.populate(fields)

        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status is None
        dataset_frame.approve_dataset_annotation(dataset.id, annotation.id)

        dataset_frame.populate(fields)
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status == "approved"

    def test_unset_qa_status_annotation(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        fields = ["annotations.id", "annotations.labels", "annotations.qa_status"]

        dataset_frame.populate(fields)

        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status == "approved"
        dataset_frame.unset_qa_status_annotation(dataset.id, annotation.id)

        dataset_frame.populate(fields)
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status is None

    def test_request_changes_annotation(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        fields = ["annotations.id", "annotations.labels", "annotations.qa_status"]

        dataset_frame.populate(fields)

        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status is None
        dataset_frame.request_changes_annotation(dataset.id, annotation.id)

        dataset_frame.populate(fields)
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status == "changesRequested"

    def test_update_qa_status_note_annotation(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        dataset_frame = frames.first()

        fields = [
            "annotations.id",
            "annotations.labels",
            "annotations.qa_status",
            "annotations.qa_status_note",
        ]

        dataset_frame.populate(fields)

        status_note = "test qa status note"
        assert len(dataset_frame.annotations) == 1
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status_note is None
        dataset_frame.update_qa_status_note_annotation(
            dataset.id, status_note, annotation.id
        )

        dataset_frame.populate(fields)
        annotation = dataset_frame.annotations[0]
        assert annotation.qa_status_note == status_note
