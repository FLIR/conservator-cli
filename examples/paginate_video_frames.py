from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

conservator = Conservator.default()
fields = FieldsRequest()
fields.include_field("video_id")
fields.include_field("width")
fields.include_field("height")
fields.include_field("annotations.bounding_box")
fields.include_field("annotations.labels")

video = conservator.videos.all().including("name", "frame_count").first()
print(video)

# Unless you're working with huge videos (10k+ frames), you'll probably
# find it easier and faster to just populate all frames at once. Only
# use this method if your request for all frames is timing out, or too large
# to handle at once.
for frame in video.get_all_frames_paginated(fields):
    print(frame)
