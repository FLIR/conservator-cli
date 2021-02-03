from FLIR.conservator.generated import schema
from FLIR.conservator.util import md5sum_file
from FLIR.conservator.wrappers.media import MediaType, MediaCompare
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
        result = MediaCompare.MISMATCH
        local_md5 = md5sum_file(local_path)
        if local_md5 == self.image_md5:
            result = MediaCompare.MATCH
        return result
