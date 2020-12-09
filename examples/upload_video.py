from FLIR.conservator.conservator import Conservator


conservator = Conservator.default()

# Conservator collection path
remote_path = f"/CLI Examples/Upload Video"

# Desired name of file in conservator:
remote_name = f"upload_video_example"

# Your local path here:
local_path = "~/datasets/flir-data/unit-test-data/videos/adas_test.mp4"

# Get collection:
collection = conservator.collections.from_remote_path(remote_path, make_if_no_exist=True, fields="id")
assert collection is not None

video = conservator.videos.upload(local_path, collection, remote_name)
video.populate_all()
print(video)