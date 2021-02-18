from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Mutation,
    FlagDatasetFrameInput,
    UnflagDatasetFrameInput,
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
            operation_base=Mutation,
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
            operation_base=Mutation,
            fields="id",
            input=input_,
        )

    def mark_empty(self):
        """
        Mark the dataset frame as empty.
        """
        return self._conservator.query(
            Mutation.mark_dataset_frame_empty,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def unmark_empty(self):
        """
        Unmake the dataset frame as empty.
        """
        return self._conservator.query(
            Mutation.unmark_dataset_frame_empty,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def approve(self):
        """
        Approve the dataset frame.
        """
        return self._conservator.query(
            Mutation.approve_dataset_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def request_changes(self):
        """
        Request changes to the dataset frame.
        """
        return self._conservator.query(
            Mutation.request_changes_dataset_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def unset_qa_status(self):
        """
        Unset the QA status of the dataset frame.
        """
        return self._conservator.query(
            Mutation.unset_qa_status_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )
