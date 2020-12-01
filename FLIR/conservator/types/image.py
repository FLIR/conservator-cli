from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy, requires_fields
from FLIR.conservator.util import download_file


class Image(TypeProxy):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images

    @requires_fields("url", "filename")
    def download(self, path):
        """Download image to ``path``."""
        download_file(path, self.filename, self.url)

