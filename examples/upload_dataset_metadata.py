# example of using API to upload annotations and QA status from local copy of dataset
#
# This is a subset of what 'cvc publish' would update; for instance,
# it does not currently add new frames or annotaitons, or update flag/unflag
# attribute of existing frames.

import argparse
import json
import logging
import os

import sgqlc.types

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.wrappers.dataset import Dataset
from FLIR.conservator.wrappers.dataset import DatasetFrame
from FLIR.conservator.connection import ConservatorGraphQLServerError
from FLIR.conservator.generated.schema import UpdateDatasetAnnotationInput


def try_commit(dataset, commit_msg):
    try:
        dataset.commit(commit_msg)
    except ConservatorGraphQLServerError as e:
        if e.errors[0]["message"] == "commit-already-queued":
            logger.info("ignore error -- commit was already queued")
        else:
            raise e


def upload_dataset_metadata(conservator_cli, local_dir, commit_msg):
    logger.info("upload metadata from local index.json")
    dataset = Dataset.from_local_path(conservator_cli, local_dir)

    # get any pending changes from web UI saved in a separate commit
    try_commit(dataset, f"commit any pending changes before: {commit_msg}")

    index_path = os.path.join(local_dir, "index.json")
    index_data = {}
    with open(index_path) as fp:
        index_data = json.load(fp)
    local_frames = index_data.get("frames", [])

    for local_frame in local_frames:
        dset_frame = DatasetFrame.from_id(
            conservator_cli, local_frame["datasetFrameId"]
        )
        dset_frame.populate("annotations")

        for local_anno in local_frame.get("annotations", []):
            # find matching annotation on server
            remote_anno = [
                anno for anno in dset_frame.annotations if anno.id == local_anno["id"]
            ]
            if not remote_anno:
                logger.info(
                    "Skipping %s annotation from %s frame (not found on server)",
                    local_anno["id"],
                    dset_frame.id,
                )
                continue

            # check to see if there are any relevant changes
            remote_anno = remote_anno[0]  # should be just one match from above search
            remote_anno = (
                remote_anno.to_json()
            )  # turn into normal dict for field compare

            for ignore_field in ("attributes", "custom_metadata", "source"):
                remote_anno.pop(ignore_field, None)
                local_anno.pop(ignore_field, None)

            if local_anno == remote_anno:
                logger.debug(
                    "No changes to %s annotation from %s frame",
                    local_anno["id"],
                    dset_frame.id,
                )
                continue

            # yes need to make changes for this annotation; pack the fields into needed format
            local_anno["dataset_annotation_id"] = local_anno[
                "id"
            ]  # id => dataset_annotation_id
            local_anno.pop("id")
            update_fields = {}
            for (key, value) in local_anno.items():
                # boundingBox -> bounding_box and so forth
                update_fields[sgqlc.types.BaseItem._to_python_name(key)] = value

            update_anno_input = UpdateDatasetAnnotationInput(**update_fields)
            dset_frame.update_dataset_annotation(update_anno_input)

        if "qaStatus" in local_frame.keys():
            if local_frame["qaStatus"] == "approved":
                logger.debug("Marking %s frame 'approved'", dset_frame.id)
                dset_frame.approve()
            elif local_frame["qaStatus"] == "changesRequested":
                qa_note = local_frame.get("qaStatusNote", "")
                logger.debug(
                    "Marking %s frame 'changesRequested' reason '%s'",
                    dset_frame.id,
                    qa_note,
                )
                dset_frame.request_changes()
                dset_frame.update_qa_status_note(qa_note)

    try_commit(dataset, commit_msg)


if __name__ == "__main__":
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    parser = argparse.ArgumentParser(
        description="uploads annotations and QA state from checked-out dataset"
    )

    parser.add_argument(
        "--dataset-dir",
        dest="dataset_dir",
        type=str,
        help="Path to dataset directory that contains index.json with metadata to upload",
        required=True,
    )
    parser.add_argument(
        "--commit-msg",
        dest="commit_msg",
        type=str,
        help="Message for committing new version of metadata",
        required=True,
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Use the named conservator-cli config instead of the default. "
        + "Run 'conservator config list' to see a list of known config names",
    )
    parser.add_argument(
        "--log_level",
        default="info",
        choices=list(log_levels.keys()),
        help="Set the logging level [%(default)s]",
    )

    args = parser.parse_args()

    conservator_cli = Conservator.create(args.config)

    # console log level is set from command-line arg
    log_format = "[%(name)s] %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_levels[args.log_level])
    logger = logging.getLogger("upload_dataset_metadata")

    upload_dataset_metadata(conservator_cli, args.dataset_dir, args.commit_msg)
