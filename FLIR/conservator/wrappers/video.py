from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.wrappers.media import MediaType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class Video(MediaType):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos

    @requires_fields("md5")
    def compare(self, local_path):
        """
        Use md5 checksums to compare video contents to local file

        Returns result as MediaCompare object

        :param local_path: Path to local copy of file for comparison with remote.
        """
        return MediaType.verify_md5(local_path, self.md5)

    def get_annotations(self, fields=None):
        """
        Returns the video's annotations with the specified `fields`.
        """
        return self._conservator.query(
            Query.annotations_by_video_id, fields=fields, id=self.id
        )

    def get_frame_by_index(self, index, fields=None):
        """
        Returns a single frame at a specific `index` in the video.
        """
        return self._query_frames(frame_index=index, fields=fields)[0]

    def get_all_frames_paginated(self, fields=None):
        """
        Yields all frames in the video, 15 at a time, using
        :meth:`get_paginated_frames`.

        This is only useful if you're dealing with very long videos
        and want to paginate frames yourself. If the video is short,
        you could just use ``populate("frames")`` to get all frames.
        """
        start = 0
        while True:
            frames = self._paginated_frames(start, fields=fields)
            yield from frames
            # frame pagination size is hard-coded to 15 in conservator
            if len(frames) < 15:
                break
            start += 15

    def _paginated_frames(self, start_index=0, fields=None):
        """
        Returns 15 frames, starting with `start_index`.
        """
        return self._query_frames(start_frame_index=start_index, fields=fields)

    def _query_frames(self, start_frame_index=None, frame_index=None, fields=None):
        fields = FieldsRequest.create(fields)

        video_fields = {
            "frames": {
                "start_frame_index": start_frame_index,
                "frame_index": frame_index,
            }
        }
        for path, value in fields.paths.items():
            new_path = "frames." + path
            video_fields[new_path] = value

        video = self._conservator.query(
            query=self.by_id_query,
            fields=video_fields,
            id=self.id,
        )
        return video.frames
