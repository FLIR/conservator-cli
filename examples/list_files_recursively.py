from FLIR.conservator.conservator import Conservator

# Unless you want to keep the media with the collections
# to be able to print the paths as in this example,
# `recursively_get_media` is a one-liner that returns
# all media recursively in a collection.

conservator = Conservator.default()

path = "/AndresTest"

starting_collection = conservator.collections.from_remote_path(
    path, fields=["path", "id"]
)
children = starting_collection.recursively_get_children(fields=["path", "id"])

all_collections = [starting_collection, *children]
for collection in all_collections:
    path = collection.path
    for video in collection.get_videos(fields=["name", "id"]):
        print(path + "/" + video.name)
    for image in collection.get_images(fields=["name", "id"]):
        print(path + "/" + image.name)

# To just print the names, using recursively_get_media:
for media in starting_collection.recursively_get_media(fields="name"):
    print(media.name)
