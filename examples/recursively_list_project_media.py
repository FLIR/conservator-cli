"""
Sample code demonstrating how to recursively retrieve
all media (i.e., videos and images) in a project/folder.
"""
from FLIR.conservator.conservator import Conservator

# Unless you want to keep the media with the collections
# to be able to print the paths as in this example,
# `recursively_get_media` is a one-liner that returns
# all media recursively in a collection.

conservator = Conservator.default()

PATH = "/AndresTest"

starting_collection = conservator.collections.from_remote_path(
    PATH, fields=["path", "id"]
)
children = starting_collection.recursively_get_children(fields=["path", "id"])

all_collections = [starting_collection, *children]
for collection in all_collections:
    PATH = collection.path
    for video in collection.get_videos(fields=["name", "id"]):
        print(PATH + "/" + video.name)
    for image in collection.get_images(fields=["name", "id"]):
        print(PATH + "/" + image.name)

# To just print the names, using recursively_get_media:
for media in starting_collection.recursively_get_media(fields="name"):
    print(media.name)
