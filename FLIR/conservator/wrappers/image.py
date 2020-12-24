from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType


class Image(MediaType):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images
