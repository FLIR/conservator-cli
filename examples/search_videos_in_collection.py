"""
Demonstrates searching for videos within a collection
"""
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.wrappers.collection import InvalidRemotePathException

conservator = Conservator.default()

# For a given location (collection) search for videos with a specific name
# the search text support all standard search logic, but we're showing an
# example where we search by the video name
CONSERVATOR_LOCATION = "/ADAS/003 Animals"
SEARCH_TEXT = 'name:"Namibia"'

try:
    # Get collection
    collection = conservator.collections.from_remote_path(
        CONSERVATOR_LOCATION, fields="id"
    )

    result_count = 0

    print(f'Matches for search: "{SEARCH_TEXT}":')
    for video in collection.recursively_get_videos(
        fields=["name", "owner"], search_text=SEARCH_TEXT
    ):
        print(video)
        result_count += 1

    if result_count == 0:
        print("   Could not find any results")
except InvalidRemotePathException:
    print(
        f"Collection at the following location does not exist: {CONSERVATOR_LOCATION}"
    )
