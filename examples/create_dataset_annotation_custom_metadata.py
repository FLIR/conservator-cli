"""
Demonstrates adding custom metadata to a dataset annotation
"""
import json

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Query

conservator = Conservator.default()

dataset_frame_id = input("Please provide a dataset frame id: ")

dataset_frame = conservator.query(
    Query.dataset_frame,
    id=dataset_frame_id,
    fields=['annotations.id']
)

dataset_annotation_id = input("Please provide a dataset annotation id: ")

# Create an object to use as metadata
metadata_obj = {
    "metadata": True,
    "meta": "data",
    "numberOfFields": 3,
}

# ... then stringify it
metadata_string = json.dumps(metadata_obj)

print(f"Adding custom metadata: {metadata_string}")

dataset_frame.set_dataset_annotation_metadata(
    annotation_id=dataset_annotation_id,
    annotation_metadata=metadata_string,
)

dataset_frame.populate(['annotations.custom_metadata'])

annotation = {}

for ann in dataset_frame.annotations:
    if ann.id == dataset_annotation_id:
        annotation = ann
        break


print("Metadata has been added!")

print(annotation)
