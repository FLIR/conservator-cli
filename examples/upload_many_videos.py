import logging

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level="INFO")
conservator = Conservator.default()

# Conservator collection path
remote_path = f"/CLI Examples/Upload Many Videos"

# Local path
local_path = "~/datasets/flir-data/unit-test-data/videos/adas_test.mp4"

# Get collection:
print("Getting collection")
collection = conservator.collections.from_remote_path(
    remote_path, make_if_no_exist=True, fields="id"
)
assert collection is not None


number_of_copies = 10
upload_tuples = [
    (local_path, f"upload_many_test_{i}") for i in range(number_of_copies)
]

print("Starting upload")
media_ids = conservator.upload_many_to_collection(upload_tuples, collection, process_count=10)
print("Created these ids:", media_ids)

print("Waiting for processing")
conservator.wait_for_processing(media_ids)

# Print out all of the media names
for media_id in media_ids:
    media = conservator.get_media_instance_from_id(media_id, fields="name")
    print(media)
