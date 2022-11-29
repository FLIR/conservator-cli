"""
Demonstrates adding custom metadata to a dataset annotation
"""
import json

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation, UpdateAnnotationInput

conservator = Conservator.default()

dataset_frame_id = input("Please provide a dataset frame id: ")

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

update_annotation_input = UpdateAnnotationInput(custom_metadata=metadata_string)

annotation = conservator.query(
    Mutation.update_dataset_annotation,
    dataset_frame_id=dataset_frame_id,
    dataset_annotation_id=dataset_annotation_id,
    input=update_annotation_input,
)

print("Metadata has been added!")

print(annotation)
