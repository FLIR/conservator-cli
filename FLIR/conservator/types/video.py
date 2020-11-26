from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy


class Video(TypeProxy):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos
