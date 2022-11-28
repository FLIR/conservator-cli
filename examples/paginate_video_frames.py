"""
A brief example showing how to retrieve video frames
"""
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

conservator = Conservator.default()

fields = FieldsRequest()
fields.include_field("frames.video_id")
fields.include_field("frames.frame_index")
fields.include_field("frames.width")
fields.include_field("frames.height")
fields.include_field("frames.annotations.bounding_box")
fields.include_field("frames.annotations.labels")

# Fields can also be retrieved by passing a list of field names:
#
# fields = ["frames.video_id",
#           "frames.width",
#           "frames.height",
#           "frames.annotations.bounding_box",
#           "frames.annotations.labels",
#           ]
#
# Note that this list will be converted into a FieldsRequest object


video = conservator.videos.all().including("name", "frame_count").first()

print(video)

# Unless you're working with huge videos (10k+ frames), you'll probably
# find it easier and faster to just populate all frames at once. Only
# use this method if your request for all frames is timing out, or too large
# to handle at once.
# This method will return 15 frames at a time
for frame in video.get_all_frames_paginated(fields):
    print(frame)
