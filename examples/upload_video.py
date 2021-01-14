import logging

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level="DEBUG")
conservator = Conservator.default()

# Conservator collection path
remote_path = f"/CLI Examples/Upload Video"

# Desired name of file in conservator:
remote_name = f"upload_video_example"

# Your local path here:
local_path = "~/datasets/flir-data/unit-test-data/videos/adas_test.mp4"

# Get collection:
print("Getting collection")
collection = conservator.collections.from_remote_path(
    remote_path, make_if_no_exist=True, fields="id"
)
assert collection is not None

print("Starting upload")
media_id = conservator.upload(local_path, collection, remote_name)

print("Waiting for processing")
conservator.wait_for_processing(media_id)

# For this example, we happen to know that the media is a Video.
# But its usually better to use get_media_from_id, as this returns
# the correct type (Image or Video instance)
media = conservator.get_media_instance_from_id(media_id)
print(media)
