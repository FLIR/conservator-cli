"""
Demonstrates adding custom metadata to a video/image annotation
"""
import json

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Query

conservator = Conservator.default()

frame_id = input("Please provide a video or image frame id: ")

frame = conservator.query(
    Query.frame_with_search, frame_id=frame_id, fields=["annotations.id"]
)

annotation_id = input("Please provide an annotation id: ")

# Create an object to use as metadata
metadata_obj = {
    "metadata": True,
    "meta": "data",
    "numberOfFields": 3,
}

# ... then stringify it
metadata_string = json.dumps(metadata_obj)

print(f"Adding custom metadata: {metadata_string}")

frame.set_annotation_metadata(annotation_id, metadata_string)

frame.populate(["annotations.custom_metadata"])

annotation = {}

for ann in frame.annotations:
    if ann.id == annotation_id:
        annotation = ann
        break


print("Metadata has been added!")

print(annotation)
