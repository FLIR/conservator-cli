from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class Image(MediaType):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images

    @requires_fields("image_md5")
    def compare(self, local_path):
        """
        Use md5 checksums to compare image contents to local file

        Returns result as MediaCompare object

        :param local_path: Path to local copy of file for comparison with remote.
        """
        return MediaType.verify_md5(local_path, self.image_md5)

    def get_frame(self, fields=None):
        """
        Get the frame of the Image. Because images only have one frame, this is
        the same as :meth:`MediaType.get_frame_by_index` with index `0`.
        """
        return self.get_frame_by_index(0, fields=fields)

