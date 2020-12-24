import json
import os

from FLIR.conservator.util import download_file
from FLIR.conservator.wrappers import QueryableType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class MediaType(QueryableType):
    """
    A media type is an image or a video. It can be uploaded (using
    :meth:``FLIR.conservator.managers.media.MediaTypeManager.upload``)
    or downloaded.
    """
    @requires_fields("metadata", "filename")
    def download_metadata(self, path):
        """
        Downloads the `metadata` field to `path/filename.json`,
        where `filename` is the media's filename.
        """
        json_data = json.loads(self.metadata)
        json_file = ".".join(self.filename.split(".")[:-1]) + ".json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(",", ": "))

    @requires_fields("url", "filename")
    def download(self, path):
        """Download video to ``path``."""
        download_file(path, self.filename, self.url)

