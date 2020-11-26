from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy


class Image(TypeProxy):
    underlying_type = schema.Image
    by_id_query = schema.Query.image
    search_query = schema.Query.images
