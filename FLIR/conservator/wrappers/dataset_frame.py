from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Mutation,
    FlagDatasetFrameInput,
    UnflagDatasetFrameInput,
    UpdateDatasetQaStatusNoteInput,
)
from FLIR.conservator.wrappers import QueryableType


class DatasetFrame(QueryableType):
    """
    A frame within a dataset.
    """

    underlying_type = schema.DatasetFrame
    by_id_query = schema.Query.dataset_frame

    def flag(self):
        """
        Flag the dataset frame.
        """
        input_ = FlagDatasetFrameInput(dataset_frame_id=self.id)
        return self._conservator.query(
            Mutation.flag_dataset_frame,
            fields="id",
            input=input_,
        )

    def unflag(self):
        """
        Unflag the dataset frame.
        """
        input_ = UnflagDatasetFrameInput(dataset_frame_id=self.id)
        return self._conservator.query(
            Mutation.unflag_dataset_frame,
            fields="id",
            input=input_,
        )

    def mark_empty(self):
        """
        Mark the dataset frame as empty.
        """
        return self._conservator.query(
            Mutation.mark_dataset_frame_empty,
            fields="id",
            id=self.id,
        )

    def unmark_empty(self):
        """
        Unmake the dataset frame as empty.
        """
        return self._conservator.query(
            Mutation.unmark_dataset_frame_empty,
            fields="id",
            id=self.id,
        )

    def approve(self):
        """
        Approve the dataset frame.
        """
        return self._conservator.query(
            Mutation.approve_dataset_frame,
            fields="id",
            id=self.id,
        )

    def request_changes(self):
        """
        Request changes to the dataset frame.
        """
        return self._conservator.query(
            Mutation.request_changes_dataset_frame,
            fields="id",
            id=self.id,
        )

    def unset_qa_status(self):
        """
        Unset the QA status of the dataset frame.
        """
        return self._conservator.query(
            Mutation.unset_qa_status_dataset_frame,
            fields="id",
            id=self.id,
        )

    def update_qa_status_note(self, qa_status_note: str):
        """
        Change the QA status note for a dataset frame.
        """
        note = UpdateDatasetQaStatusNoteInput(id=self.id, qa_status_note=qa_status_note)
        return self._conservator.query(
            Mutation.update_dataset_qa_status_note, input=note
        )

    def add_annotations(self, annotation_create_list, fields=None):
        """
        Adds annotations using the specified list of `CreateDatasetAnnotationInput`
        objects.

        Returns a list of the added annotations, each with the specified
        `fields`.
        """
        if annotation_create_list:
            for anno in annotation_create_list:
                anno["dataset_frame_id"] = self.id

            return self._conservator.query(
                Mutation.create_dataset_annotations,
                fields=fields,
                input=annotation_create_list,
            )
        # If supplied an empty list, return the same.
        return []

    def update_annotation(self, annotation, fields=None):
        """
        Updates existing annotation using the specified `UpdateDatasetAnnotationInput`
        object.

        Returns updated annotation with the specified `fields`.
        """
        return self._conservator.query(
            Mutation.update_dataset_annotation,
            fields=fields,
            dataset_frame_id=self.id,
            input=annotation,
        )

    def approve_annotation(self, annotation_id):
        """
        Approve an annotation within dataset frame.
        """
        return self._conservator.query(
            Mutation.approve_dataset_annotation,
            fields=("id", "qa_status"),
            dataset_frame_id=self.id,
            annotation_id=annotation_id,
        )

    def request_changes_annotation(self, annotation_id):
        """
        Request changes to an annotation within dataset frame.
        """
        return self._conservator.query(
            Mutation.request_changes_dataset_annotation,
            fields=("id", "qa_status"),
            dataset_frame_id=self.id,
            annotation_id=annotation_id,
        )

    def unset_qa_status_annotation(self, annotation_id):
        """
        Unset the QA status of an annotation within dataset frame.
        """
        return self._conservator.query(
            Mutation.unset_qa_status_dataset_annotation,
            fields=("id", "qa_status"),
            dataset_frame_id=self.id,
            annotation_id=annotation_id,
        )

    def update_qa_status_note_annotation(self, qa_status_note: str, annotation_id):
        """
        Change the QA status note for an annotation within dataset frame.
        """
        return self._conservator.query(
            Mutation.update_qa_status_note_dataset_annotation,
            fields=("id", "qa_status"),
            dataset_frame_id=self.id,
            annotation_id=annotation_id,
            qa_status_note=qa_status_note,
        )
