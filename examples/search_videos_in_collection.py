from FLIR.conservator.conservator import Conservator
import FLIR.conservator
from FLIR.conservator.wrappers import Video

conservator = Conservator.default()

# For a given location (collection) search for videos with a specific name
# the search text support all standard search logic, but we're showing an example where we search by the video name
conservator_location = '/ADAS/003 Animals'
search_filename = 'Namibia'
search_text = f'name:"{search_filename}"'

try:
    # Get collection
    collection = conservator.collections.from_remote_path(
        conservator_location,
        fields="id"
    )

    result_count = 0
    print(f'Matches for search: "{search_text}":')
    for video in collection.recursively_get_videos(fields=["name", "owner"], search_text=search_text):
        video: Video
        print(video)
        result_count += 1

    if result_count == 0:
        print('   Could not find any results')
except FLIR.conservator.wrappers.collection.InvalidRemotePathException:
    print(f'Collection at the following location does not exist: {conservator_location}')
