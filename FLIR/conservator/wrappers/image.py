from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType


class Image(MediaType):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images

    def get_frames(self, index, start_index, custom_metadata, fields=None):
        """
        Returns the image's frames, with the specified `fields`.
        """
        return self._conservator.query(
            schema.Image.frames,
            operation_base=schema.Image,
            fields=fields,
            id=self.id,
            frame_index=index,
            start_frame_index=start_index,
            custom_metadata=custom_metadata,
        )
