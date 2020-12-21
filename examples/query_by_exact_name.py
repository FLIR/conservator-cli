from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

video_name = "00965760_cam2.avi"

# The "name" field is searched by default, but we need to add a filter
# to make sure that the name is an exact match. Searches only check for
# substring containment, so searching "my video" would match "my video"
# and also something like "my video TEST".

# With filtered_by, we make sure to only return videos where the name is
# an exact match.
print("Normal search:")
results = conservator.videos.search(video_name, fields="name").filtered_by(
    name=video_name
)
for video in results:
    assert video.name == video_name
    print(video)

print()
print("Search by name field only:")
# We could also slightly speed up the query using Conservator's Advanced
# Search syntax. We can specify which field to search in the search text:
results = conservator.videos.search(f'name:"{video_name}"', fields="name").filtered_by(
    name=video_name
)
for video in results:
    assert video.name == video_name
    print(video)
