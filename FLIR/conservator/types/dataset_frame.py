from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Mutation,
    FlagDatasetFrameInput,
    UnflagDatasetFrameInput,
)
from FLIR.conservator.types import QueryableType


class DatasetFrame(QueryableType):
    underlying_type = schema.DatasetFrame
    by_id_query = schema.Query.dataset_frame

    def flag(self):
        input_ = FlagDatasetFrameInput(dataset_frame_id=self.id)
        self._conservator.query(
            Mutation.flag_dataset_frame,
            operation_base=Mutation,
            fields="id",
            input=input_,
        )

    def unflag(self):
        input_ = UnflagDatasetFrameInput(dataset_frame_id=self.id)
        self._conservator.query(
            Mutation.unflag_dataset_frame,
            operation_base=Mutation,
            fields="id",
            input=input_,
        )

    def mark_empty(self):
        self._conservator.query(
            Mutation.mark_dataset_frame_empty,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def unmark_empty(self):
        self._conservator.query(
            Mutation.unmark_dataset_frame_empty,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def approve(self):
        self._conservator.query(
            Mutation.approve_dataset_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def request_changes(self):
        self._conservator.query(
            Mutation.request_changes_dataset_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )

    def unset_qa_status(self):
        self._conservator.query(
            Mutation.unset_qa_status_frame,
            operation_base=Mutation,
            fields="id",
            id=self.id,
        )
