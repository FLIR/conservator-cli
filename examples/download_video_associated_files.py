import os

from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

video_id = input("Please provide a video id: ")

video = conservator.videos.from_id(video_id)

video_dir = os.path.expanduser(f'~/associated_files/{video_id}')

video.download_associated_files(video_dir)
