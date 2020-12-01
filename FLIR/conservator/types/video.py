import json
import os

from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy, requires_fields
from FLIR.conservator.util import download_file


class Video(TypeProxy):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos

    @requires_fields("metadata", "filename")
    def download_metadata(self, path):
        json_data = json.loads(self.metadata)
        json_file = ".".join(self.filename.split(".")[:-1]) + ".json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(',', ': '))

    @requires_fields("url", "filename")
    def download(self, path):
        """Download video to ``path``."""
        download_file(path, self.filename, self.url)

