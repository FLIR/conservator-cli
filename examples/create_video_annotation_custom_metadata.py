"""
Demonstrates adding custom metadata to a video/image annotation
"""
import json

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation, UpdateAnnotationInput

conservator = Conservator.default()

frame_id = input("Please provide a video or image frame id: ")

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

update_annotation_input = UpdateAnnotationInput(custom_metadata=metadata_string)

annotation = conservator.query(
    Mutation.update_annotation,
    frame_id=frame_id,
    annotation_id=annotation_id,
    annotation=update_annotation_input,
)

print("Metadata has been added!")

print(annotation)
