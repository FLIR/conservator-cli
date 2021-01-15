import logging

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level="INFO")
conservator = Conservator.default()

# Conservator collection path
remote_path = f"/CLI Examples/Upload Many Videos"

# Local path. This example will upload the file at this path 10 times.
local_path = "~/datasets/flir-data/unit-test-data/videos/adas_test.mp4"
number_of_copies = 10

# Get collection:
print("Getting collection")
collection = conservator.collections.from_remote_path(
    remote_path, make_if_no_exist=True, fields="id"
)
assert collection is not None

# When you upload things in parallel, you need to create a list
# of the files to upload. You can either a list of the individual
# file paths, or a list of tuples containing (file_path, remote_name).
# The first option will use the local file name for the remote name, and
# is probably perfect for most use cases. However in this example we want
# our remote names to be unique:
upload_tuples = [(local_path, f"upload_many_test_{i}") for i in range(number_of_copies)]

print("Starting upload")
media_ids = conservator.upload_many_to_collection(
    upload_tuples, collection=collection, process_count=10
)
print("Created these ids:", media_ids)

print("Waiting for processing")
conservator.wait_for_processing(media_ids)

# Print out all of the media names
for media_id in media_ids:
    media = conservator.get_media_instance_from_id(media_id, fields="name")
    print(media)
