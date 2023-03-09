#!/usr/bin/env python
"""Demonstrate applying dataset annotation QA status from JSON data."""

import argparse
import json
import sys

from typing import Any, Dict, List

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.wrappers.dataset_frame import DatasetFrame
from FLIR.conservator.generated.schema import DatasetAnnotation, UpdateAnnotationInput


# JSON format
# {
#   "dataset_id": string,
#   "changes": {
#       "frame_ids": [
#           {
#               "<dataset_frame_id>": {
#                   "annotation_ids": [
#                       {
#                           "<annotation_id>": {
#                               -- one or more of:
#                               "labels": list of strings,
#                               "label_id": string,
#                               "qa_status": "approved" | "changesRequested",
#                               "qa_status_note": string,
#                               "target_id": number,
#                               "custom_metadata": JSON string
#                           }
#                       },
#                       ...
#                   ]
#               }
#           },
#           ...
#       ]
#   }
# }
#

ANNOTATION_UPDATE_DATA = {
    "dataset_id": "jDm7G7sNrtz7jvmd3",
    "changes": {
        "frame_ids": [
            {
                "Nj2kArRmD7vNtBSq3": {
                    "annotation_ids": [{"GHcKguB5iaQob2fSw": {"target_id": 1}}]
                }
            },
            {
                "EjMLzi5YD3KRcf6qy": {
                    "annotation_ids": [
                        {
                            "eenEYGmSbRfC79vbK": {
                                "target_id": 1,
                                "qa_status": "approved",
                            }
                        }
                    ]
                }
            },
        ]
    },
}


UPDATE_FIELD_NAMES = [
    "labels",
    "label_id",
    "qa_status",
    "qa_status_note",
    "target_id",
    "custom_metadata",
]


def apply_changes(conservator_instance, dataset_id, change_list):
    """Apply the given list of valid dataset frame annotation updates."""
    for a_change in change_list:
        dframe = DatasetFrame.from_id(
            conservator_instance, a_change["dataset_frame_id"]
        )
        update_data = dict(a_change["data"])
        for a_key in a_change["data"]:
            if a_key.startswith("qa"):
                del update_data[a_key]
        # Handle non-QA-related changes using the update method.
        if update_data:
            update_input = UpdateAnnotationInput(**update_data)
            print(
                f"Update dataset frame annotation id {a_change['annotation_id']} with data {update_data}"
            )
            dframe.update_dataset_annotation(update_input, a_change["annotation_id"])
        # Handle QA using QA-specific methods.
        if "qa_status" in a_change["data"]:
            if a_change["data"]["qa_status"] == "approved":
                print(
                    f"Approve dataset frame annotation id {a_change['annotation_id']}"
                )
                dframe.approve_dataset_annotation(dataset_id, a_change["annotation_id"])
            else:
                print(
                    f"Request changes for dataset frame annotation id {a_change['annotation_id']}"
                )
                dframe.request_changes_annotation(dataset_id, a_change["annotation_id"])
        if "qa_status_note" in a_change["data"]:
            print(f"Set status note '{a_change['data']['qa_status_note']}'")
            dframe.update_qa_status_note_annotation(
                dataset_id,
                a_change["data"]["qa_status_note"],
                a_change["annotation_id"],
            )


def get_annotation_list_updates(
    frame_annotations: List[Dict[str, Any]],
    frame_id: str,
    annotation_obj_list: List[Dict[str, Any]],
):
    """
    Collect a valid set of updates from a list of annotation changes.

    :param frame_annotations: Current list of dataset frame annotation data
    :param frame_id: The dataset frame ID containing annotations to be changed
    :param annotation_obj_list: List of annotation change data objects
    """
    apply_list = []
    found_anno = None
    for anno_obj in annotation_obj_list:
        for anno_id, anno_data in anno_obj.items():
            apply_entry = {"dataset_frame_id": frame_id, "annotation_id": anno_id}
            change_params = {}
            for an_anno in frame_annotations:
                if an_anno["id"] == anno_id:
                    found_anno = an_anno
                    break
            if found_anno is None:
                print("ERROR: Invalid annotation id '" + anno_id + "'")
                sys.exit(1)
            for key, val in anno_data.items():
                if key in UPDATE_FIELD_NAMES:
                    change_params[key] = val
                else:
                    print(f"WARNING: skipping unknown field name '{key}'")
            if not change_params:
                print("WARNING: No changes supplied for annotation '" + anno_id + "'")
                continue
            # Check whether this annotation has already been updated.
            update_params = {}
            for ch_key, ch_val in change_params.items():
                gql_name = getattr(DatasetAnnotation, ch_key).graphql_name
                if (gql_name not in found_anno) or (found_anno[gql_name] != ch_val):
                    old_val = found_anno.get(gql_name, "none")
                    print(f"Update field {ch_key}: {old_val} -> {ch_val}")
                    update_params[ch_key] = ch_val
            if not update_params:
                print(
                    f"Skipping up-to-date annotation ID {apply_entry['annotation_id']}"
                )
                continue
            apply_entry["data"] = update_params
            apply_list.append(apply_entry)
    return apply_list


def update_annotations(conservator_instance, json_data, commit_message, dry_run):
    """Update dataset frame annotations using JSON-formatted data."""
    if "dataset_id" not in json_data:
        print("ERROR: Missing 'dataset_id' field in supplied JSON update data.")
        sys.exit(1)
    if "changes" not in json_data:
        print("ERROR: Missing 'changes' field in supplied JSON update data.")
        sys.exit(1)
    if "frame_ids" not in json_data["changes"]:
        print(
            "ERROR: No frame ID list found in 'changes' field in supplied JSON update data."
        )
        sys.exit(1)

    dataset_id = json_data["dataset_id"]
    dataset = None
    for dset in conservator_instance.datasets.search("id:" + '"' + dataset_id + '"'):
        dataset = dset
    if dataset is None:
        print(f"ERROR: Unable to find dataset with ID: '{dataset_id}'")
        sys.exit(1)

    apply_list = []
    frame_fields = [
        "dataset_frames.id",
        "dataset_frames.annotations.id",
        "dataset_frames.annotations.labels",
        "dataset_frames.annotations.label_id",
        "dataset_frames.annotations.qa_status",
        "dataset_frames.annotations.qa_status_note",
        "dataset_frames.annotations.target_id",
        "dataset_frames.annotations.custom_metadata",
    ]
    frame_annotation_data = [
        a_frame.to_json() for a_frame in dataset.get_frames(fields=frame_fields)
    ]
    for frame_id_entry in json_data["changes"]["frame_ids"]:
        for frame_id, frame_obj in frame_id_entry.items():
            found_frame = None
            for a_frame in frame_annotation_data:
                if a_frame["id"] == frame_id:
                    found_frame = a_frame
                    break
            if found_frame is None:
                print("ERROR: Invalid dataset frame id '" + frame_id + "'")
                sys.exit(1)
            if not "annotation_ids" in frame_obj:
                print(
                    f"WARNING: No annotation IDs found for frame ID '{frame_id}', skipping .."
                )
                continue
            apply_list += get_annotation_list_updates(
                found_frame["annotations"], frame_id, frame_obj["annotation_ids"]
            )
    if not dry_run:
        if not apply_list:
            print("All annotations up-to-date.")
            return False
        print(f"Applying {len(apply_list)} annotation updates..")
        apply_changes(conservator_instance, dataset_id, apply_list)
        if len(commit_message) > 0:
            print(
                f"Committing changes to dataset with commit message: '{commit_message}'"
            )
            dataset.commit(commit_message)
    return True


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Update dataset frame annotations")
    PARSER.add_argument(
        "--commit_message",
        type=str,
        default="",
        help="Commit changes with the supplied message if successful",
    )
    PARSER.add_argument(
        "--config",
        type=str,
        default="default",
        help="Select a conservator_cli config to use in place of the default",
    )
    PARSER.add_argument(
        "--from_json_file", help="Supply a JSON-formatted file with annotation data"
    )
    PARSER.add_argument(
        "--dry_run",
        action="store_true",
        help="Check JSON data, but don't apply or commit changes",
    )
    ARGS = PARSER.parse_args()

    UPDATE_DATA = ANNOTATION_UPDATE_DATA
    if ARGS.from_json_file:
        UPDATE_DATA = json.load(ARGS.from_json_file)

    INSTANCE = Conservator.create(ARGS.config)
    APPLIED = update_annotations(
        INSTANCE, UPDATE_DATA, ARGS.commit_message, ARGS.dry_run
    )
