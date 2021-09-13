import sys
import logging
import os.path as osp

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level="INFO")

# Use either a named configuration
# conservator = Conservator.create('local')
# Or instead of a named configuration rely on the default which was created with `conservator config create default`
conservator = Conservator.default()

# Conservator collection path
remote_path = f"/CLI Examples/Upload Video"

# Desired name of file in conservator:
remote_name = f"upload_video_example"

# Your local path here:
local_path = osp.abspath(
    osp.join(osp.dirname(__file__), "../test/data/mp4/adas_thermal.mp4")
)

# Get collection:
print("Getting collection")
collection = conservator.collections.from_remote_path(
    remote_path, make_if_no_exist=True, fields="id"
)
assert collection is not None

print("Starting upload")
media_id = conservator.videos.upload(
    local_path, collection=collection, remote_name=remote_name
)
if not media_id:
    print("Upload failed")
    sys.exit(1)

print("Waiting for processing")
conservator.videos.wait_for_processing(media_id)

# For this example, we happen to know that the media is a Video.
# But its usually better to use get_media_from_id, as this returns
# the correct type (Image or Video instance)
media = conservator.get_media_instance_from_id(media_id)
print(media)
