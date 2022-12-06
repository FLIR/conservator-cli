"""
Brief script that demonstrates how to use the GraphQL API to
perform QA operations on a dataset annotation
"""
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation

conservator = Conservator.default()

dataset_id = input("Please provide a dataset id:")

dataset_frame_id = input("Please provide a dataset frame id: ")

annotation_id = input("Please provide a dataset annotation id: ")

annotation = conservator.query(
    Mutation.request_changes_dataset_annotation,
    dataset_id=dataset_id,
    dataset_frame_id=dataset_frame_id,
    annotation_id=annotation_id,
)

print("Changes have been requested!")
print(annotation)

request_changes_note = input("Add a note on your annotation change request: ")

annotation = conservator.query(
    Mutation.update_qa_status_note_dataset_annotation,
    dataset_id=dataset_id,
    dataset_frame_id=dataset_frame_id,
    annotation_id=annotation_id,
    qa_status_note=request_changes_note,
)

print("Note has been added!")

print(annotation)

# Calling this API a will unset the dataset annotation's QA status
#
# annotation = conservator.query(
#     Mutation.unset_qa_status_dataset_annotation,
#     dataset_id=dataset_id,
#     dataset_frame_id=dataset_frame_id,
#     annotation_id=annotation_id,
# )

# Calling this API will approve a dataset annotation
#
# annotation = conservator.query(
#     Mutation.approve_dataset_annotation,
#     dataset_id=dataset_id,
#     dataset_frame_id=dataset_frame_id,
#     annotation_id=annotation_id,
# )
#
