"""
Demonstrates QA actions on a video/image annotation
"""
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation, UpdateQaStatusNoteInput

conservator = Conservator.default()

annotation_id = input("Please provide an annotation id: ")

annotation = conservator.query(Mutation.request_changes_annotation, id=annotation_id)

print("Changes have been requested!")
print(annotation)

request_changes_note = input("Add a note on your annotation change request: ")

annotation = conservator.query(
    Mutation.update_qa_status_note_annotation,
    input=UpdateQaStatusNoteInput(
        id=annotation_id, qa_status_note=request_changes_note
    ),
)

print("Note has been added!")

print(annotation)

# To approve an annotation:
# annotation = conservator.query(
#     Mutation.approve_annotation,
#     id=annotation_id,
# )

# To unset qa status on an annotation:
# annotation = conservator.query(
#     Mutation.unset_qa_status_annotation,
#     id=annotation_id,
# )
