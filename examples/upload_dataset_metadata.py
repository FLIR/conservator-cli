# example of using API to upload annotations and QA status from local copy of dataset
#
# This is a subset of what 'cvc publish' would update; for instance,
# it does not currently add new frames or update flag/unflag attribute of
# existing frames.

import argparse
import json
import logging
import os

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.wrappers.dataset import Dataset
from FLIR.conservator.wrappers.dataset import DatasetFrame
from FLIR.conservator.connection import ConservatorGraphQLServerError


def try_commit(dataset, commit_msg):
    try:
        dataset.commit(commit_msg)
    except ConservatorGraphQLServerError as e:
        if e.errors[0]["message"] == "commit-already-queued":
            logger.info("ignore error -- commit was already queued")
        else:
            raise e


def upload_dataset_annotations(conservator_cli, local_dir, commit_msg):
    logger.info("upload annotations from local index.json")
    dataset = Dataset.from_local_path(conservator_cli, local_dir)

    index_path = os.path.join(local_dir, "index.json")
    dataset.upload_metadata(index_path)


def upload_dataset_qa(conservator_cli, local_dir, commit_msg):
    logger.info("upload QA from local index.json")
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
        for anno in local_frame.get("annotations", []):
            if "qaStatus" in anno.keys():
                anno_id = anno["id"]
                if anno["qaStatus"] == "approved":
                    logger.debug("Marking %s annotation 'approved'", anno_id)
                    dset_frame.approve_annotation(anno_id)
                elif anno["qaStatus"] == "changesRequested":
                    qa_note = anno.get("qaStatusNote", "")
                    logger.debug(
                        "Marking %s annotation 'changesRequested' reason '%s'",
                        anno_id,
                        qa_note,
                    )
                    dset_frame.request_changes_annotation(anno_id)
                    dset_frame.update_qa_status_note_annotation(qa_note, anno_id)

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

    try_commit(dataset, f"commit any QA changes for: {commit_msg}")


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

    upload_dataset_qa(conservator_cli, args.dataset_dir, args.commit_msg)
    upload_dataset_annotations(conservator_cli, args.dataset_dir, args.commit_msg)
