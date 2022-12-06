"""
Sample code for downloading multiple videos
"""
import os

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.file_transfers import DownloadRequest

conservator = Conservator.default()

# this will be the base directory where videos will be downloaded.
download_path = os.path.join(os.getcwd(), "videos")

# search text can use FLIR advanced search syntax
SEARCH_TEXT = "location:Goleta AND has:car"

# we will need filename and url to do a download,
# and md5sum allows optimization of skipping files that are already
# valid copies of the remote file
fields = ["filename", "url", "md5"]

# we create a query for videos with our search text and fields:
videos = conservator.videos.search(SEARCH_TEXT).with_fields(fields)

# you could easily download the videos one at a time using
# `Video.download(path)`

# for video in videos:
#     video.download(download_path)


# but it is going to be faster to download multiple at once.
# we use Conservator.files.download_many to do so.
# this takes a list of DownloadRequest named tuples.
files = []
for video in videos:
    print(video.filename)
    path = os.path.join(download_path, video.filename)
    file = DownloadRequest(url=video.url, local_path=path, expected_md5=video.md5)
    files.append(file)

# By providing expected md5s, files won't be re-downloaded if they
# exist at the path and match the hash.
conservator.files.download_many(files)
