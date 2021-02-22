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
