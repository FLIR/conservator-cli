from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

path = "/AndresTest"

starting_collection = conservator.collections.from_remote_path(path, fields="path")
collections = [starting_collection]

while len(collections) > 0:
    collection = collections.pop()
    path = collection.path
    for video in collection.get_videos(fields="name"):
        print(path + "/" + video.name)
    for image in collection.get_videos(fields="name"):
        print(path + "/" + image.name)
    collection.populate(["children.path", "children.id"])
    collections.extend(collection.children)
