import json
import os

from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.type_proxy import requires_fields
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.util import download_file


class Image(QueryableType):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images

    @requires_fields("metadata", "filename")
    def download_metadata(self, path):
        """
        Downloads the `metadata` field to `path/filename.json`,
        where `filename` is the video's filename.
        """
        json_data = json.loads(self.metadata)
        json_file = ".".join(self.filename.split(".")[:-1]) + ".json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(",", ": "))

    @requires_fields("url", "filename")
    def download(self, path):
        """Download image to ``path``."""
        download_file(path, self.filename, self.url)
