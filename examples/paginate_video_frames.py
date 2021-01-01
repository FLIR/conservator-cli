from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

conservator = Conservator.default()
fields = FieldsRequest()
fields.include_field("video_id")
fields.include_field("width")
fields.include_field("height")
fields.include_field("annotations.bounding_box")
fields.include_field("annotations.labels")

video = conservator.videos.all().including("name", "frames_count").first()
print(video)


# Unless you're working with huge videos (10k+), you'll probably find
# it easier and faster to just populate all frames at once. Only
# use this if your request for all frames is timing out, or too large
# to handle at once.


def paginate_video_frames(vid):
    start = 0
    while True:
        frames = vid.get_paginated_frames(start, fields=fields)
        yield from frames
        # frame pagination size is hard-coded to 15 in conservator
        if len(frames) < 15:
            break
        start += 15


for frame in paginate_video_frames(video):
    print(frame)
