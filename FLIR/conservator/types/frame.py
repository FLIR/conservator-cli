from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import AnnotationCreate, Mutation, PredictionCreate
from FLIR.conservator.types.type_proxy import TypeProxy, requires_fields
from FLIR.conservator.util import download_file


class Frame(TypeProxy):
    underlying_type = schema.Frame
    search_query = schema.Query.images
    by_ids_query = schema.Query.frames_by_ids

    @requires_fields("url", "filename")
    def download(self, path):
        """Download image to ``path``."""
        download_file(path, self.filename, self.url)

    def _populate(self, fields):
        ids = [self.id]
        return self._conservator.query(Frame.by_ids_query, fields=fields,
                                       ids=ids)[0]

    def get_annotations(self, fields=None):
        """
        Returns the frame's annotations with the specified `fields`.
        """
        return self._conservator.query(schema.Frame.annotations, operation_base=schema.Frame,
                                       fields=fields, id=self.id)

    def add_annotation(self, annotation_create, fields=None):
        """
        Adds an annotation using the specified `annotation_create` object.

        Returns the added annotation with the specified `fields`.
        """
        assert isinstance(annotation_create, AnnotationCreate)
        return self._conservator.query(Mutation.create_annotation, operation_base=Mutation,
                                       fields=fields,
                                       frame_id=self.id, annotation=annotation_create)

    def add_prediction(self, prediction_create, fields=None):
        """
        Adds a prediction using the specified `annotation_create` object.

        Returns the added prediction with the specified `fields`.
        """
        assert isinstance(prediction_create, PredictionCreate)
        return self._conservator.query(Mutation.create_prediction, operation_base=Mutation,
                                       fields=fields,
                                       frame_id=self.id, prediction=prediction_create)
