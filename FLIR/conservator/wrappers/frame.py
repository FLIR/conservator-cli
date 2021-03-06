import os

from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    AnnotationCreate,
    Mutation,
    PredictionCreate,
)
from FLIR.conservator.wrappers import QueryableType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class Frame(QueryableType):
    """
    A frame within a media object (image or video).
    """

    underlying_type = schema.Frame
    by_ids_query = schema.Query.frames_by_ids

    @requires_fields("url", "video_name", "frame_index", "md5")
    def download(self, path, no_meter=False):
        """
        Download media under the directory `path`. The filename will be ``[media id]-[frame index].jpg``,
        where `media id` is the id of the media this frame is a part of, and `frame index` is zero
        padded to 6 digits.
        """
        name = f"{self.video_id}-{self.frame_index:06d}.jpg"
        local_path = os.path.join(path, name)
        self._conservator.files.download_if_missing(
            url=self.url,
            local_path=local_path,
            expected_md5=self.md5,
            no_meter=no_meter,
        )

    def _populate(self, fields):
        ids = [self.id]
        return self._conservator.query(Frame.by_ids_query, fields=fields, ids=ids)[0]

    def add_annotation(self, annotation_create, fields=None):
        """
        Adds an annotation using the specified `annotation_create` object.

        Returns the added annotation with the specified `fields`.
        """
        assert isinstance(annotation_create, AnnotationCreate)
        return self._conservator.query(
            Mutation.create_annotation,
            fields=fields,
            frame_id=self.id,
            annotation=annotation_create,
        )

    def add_prediction(self, prediction_create, fields=None):
        """
        Adds a prediction using the specified `prediction_create` object.

        Returns the added prediction with the specified `fields`.
        """
        assert isinstance(prediction_create, PredictionCreate)
        return self._conservator.query(
            Mutation.create_prediction,
            fields=fields,
            frame_id=self.id,
            prediction=prediction_create,
        )
