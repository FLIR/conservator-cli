import os

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.util import download_files

conservator = Conservator.default()

# this will be the base directory where videos will be downloaded.
download_path = os.path.join(os.getcwd(), "videos")

# search text can use FLIR advanced search syntax
search_text = "location:Goleta AND has:car"

# we will need filename and url to do a download
fields = ["filename", "url"]

# we create a query for videos with our search text and fields:
videos = conservator.videos.search(search_text).with_fields(fields)

# you could easily download the videos one at a time using
# `Video.download(path)`
"""
for video in videos:
    video.download(download_path)
"""

# but it is going to be faster to download multiple at once.
# we use the utility function `download_files` to do so.
# this takes a list of (dir_path, filename, url) tuples.
files = []
for video in videos:
    print(video.filename)
    file = (download_path, video.filename, video.url)
    files.append(file)

download_files(files)
