from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType


class Image(MediaType):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images

    def get_frame(self, fields=None):
        """
        Get the frame of the Image. Because images only have one frame, this is
        the same as :meth:`MediaType.get_frame_by_index` with index `0`.
        """
        frame_filter = schema.FrameFilter(video_id=self.id, frame_index=0)

        image = self._conservator.query(
            query=schema.Query.frame, filter=frame_filter, fields=fields
        )

        return image
