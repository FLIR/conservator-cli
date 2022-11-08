from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType


class Video(MediaType):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos

    def get_frames(self, fields=None):
        """
        Get the video's frames
        """
        frame_filter = schema.FrameFilter(video_id=self.id)

        query_fields = fields

        if query_fields is None:
            query_fields = ["frames"]
        elif not "frames" in query_fields:
            query_fields.append("frames")

        frames = self._conservator.query(
            query=schema.Query.frames, filter=frame_filter, limit=0, fields=query_fields
        )

        return frames.frames
