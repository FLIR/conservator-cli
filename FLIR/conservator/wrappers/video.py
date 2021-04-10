from FLIR.conservator.generated import schema
from FLIR.conservator.wrappers.media import MediaType


class Video(MediaType):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos
