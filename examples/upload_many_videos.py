"""
Example of how to upload multiple videos to a folder in parallel
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Conservator collection path
FOLDER_PATH = "/CLI Examples/Upload Many Videos"

# Local path. This example will upload the file at this path 10 times.
FILE_PATH = "~/datasets/flir-data/unit-test-data/videos/adas_test.mp4"
NO_OF_COPIES = 10

# Get collection:
print("Getting collection")
collection = conservator.collections.from_remote_path(
    FOLDER_PATH, make_if_no_exist=True, fields="id"
)
assert collection is not None

# When you upload things in parallel, you need to create a list
# of the files to upload. You can either a list of the individual
# file paths, or a list of tuples containing (file_path, remote_name).
# The first option will use the local file name for the remote name, and
# is probably perfect for most use cases. However in this example we want
# our remote names to be unique:
upload_tuples = [(FILE_PATH, f"upload_many_test_{i}") for i in range(NO_OF_COPIES)]

print("Starting upload")
media_ids = conservator.videos.upload_many_to_collection(
    upload_tuples, collection=collection, process_count=10
)
print("Created these ids:", media_ids)

print("Waiting for processing")
conservator.videos.wait_for_processing(media_ids)

# Print out all of the media names
for media_id in media_ids:
    media = conservator.get_media_instance_from_id(media_id, fields="name")
    print(media)
