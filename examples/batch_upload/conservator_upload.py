# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=broad-except
"""
Script to upload videos with metadata to a Conservator instance
"""
import argparse
import csv
import json
import logging
import os
import os.path as osp
import sys
from prettytable import PrettyTable

# Local
from utils.load_json import load_json
from utils.default_metadata import DefaultMetadata
from utils.config_reader import read_subfolder_config
from utils.color_logging import CustomFormatter
from utils.upload_helpers import Uploader, Stats
import FLIR.conservator.conservator
from FLIR.conservator.conservator import Conservator

# -------------------
#   Description
# -------------------
#  Upload data to Conservator
DEFAULT_UPLOAD_CONFIG_ROOT = osp.join(
    osp.dirname(osp.realpath(__file__)), "config", "upload"
)

os.environ["BASE_DIR"] = osp.dirname(osp.realpath(__file__))

_UPLOAD_TYPE_VIDEO = "video"
_UPLOAD_TYPE_IMAGES = "images"
_UPLOAD_TYPE_PRISM = "prism"

# -------------------------------------
#               Logging
# -------------------------------------
_logger: logging.Logger = logging.getLogger("upload")
_logger.setLevel(logging.INFO)
_ch = logging.StreamHandler()
_ch.setFormatter(CustomFormatter())
_logger.addHandler(_ch)
FLIR.conservator.conservator.logger.setLevel(logging.DEBUG)

# -------------------------------------
#               Stats
# -------------------------------------
def show_help(default_config_path: str, config_filename: str) -> None:
    """
    :param default_config_path: root path to configs
    :param config_filename: name of config file
    :return: None
    """
    help_table = PrettyTable(["Config", "Description"])
    help_table.align = "l"

    config_folders = sorted(os.listdir(default_config_path))

    for config_folder in config_folders:
        config_folder_path = osp.join(default_config_path, config_folder)
        if not osp.isdir(config_folder_path):
            continue

        config_path = osp.join(config_folder_path, config_filename)

        if not osp.exists(config_path):
            continue

        with open(config_path, encoding="UTF-8") as config_file:
            try:
                config_data = json.load(config_file)
            except json.decoder.JSONDecodeError as e:
                _logger.warning(f'Could not parse JSON file: "{config_path}" with error: {e}')

            help_table.add_row([config_folder, config_data.get("description", "")])
    print(help_table)
    sys.exit(1)


def main_helper(args, upload_config_root: str, logger: logging.Logger, dry_run: bool):

    # -------------------------------------
    #        Conservator CLI
    # -------------------------------------
    conservator: Conservator = Conservator.default()

    config_filename = "upload.json"
    config_path = read_subfolder_config(
        args, upload_config_root, config_filename, show_help=show_help, logger=logger
    )
    upload_config_name = osp.basename(osp.dirname(config_path))

    config = load_json(config_path)

    default_metadata_dict = {}
    for hardware_name, default_metadata in config["default_metadata"].items():
        default_metadata_dict[hardware_name] = DefaultMetadata(
            default_metadata, hardware_name
        )

    upload_list_path = osp.join(upload_config_root, upload_config_name, "upload.csv")

    if not osp.exists(upload_list_path):
        logger.fatal(
            f"missing upload list CSV file. Expected it here: {upload_list_path}"
        )
        sys.exit(1)

    stats = Stats()
    uploader = Uploader(logger, conservator, stats)

    with open(upload_list_path, encoding="UTF-8") as list_data_file:
        reader = csv.DictReader(list_data_file)

        for row in reader:
            row: dict
            stats.upload_entry_count += 1
            upload_type = str(row["type"]).lower()

            if len(upload_type) > 0 and upload_type[0] == "#":
                stats.upload_entry_commented_out_count += 1
                continue

            hardware_name = str(row["hardware_name"]).lower()
            camera_name_or_spectrum = None
            if upload_type in [_UPLOAD_TYPE_VIDEO, _UPLOAD_TYPE_IMAGES]:
                # Extract camera name (or spectrum) from the hardware_name field
                if "." in hardware_name:
                    parts = hardware_name.split(".")
                    hardware_name = parts[0]
                    camera_name_or_spectrum = parts[1]
                else:
                    camera_name_or_spectrum = "default"

            if isinstance(row.get("tags"), str):
                row["tags"] = row["tags"].strip()
                if len(row["tags"]):
                    tags_split = row["tags"].split(",")  # Always outputs a list
                    tags: list = []
                    for tag in tags_split:
                        tags.append(tag.strip().lower())
                    row["tags"] = tags
                else:
                    row["tags"] = []
            else:
                row["tags"] = []

            if not isinstance(row.get("location"), str):
                row["location"] = ""

            conservator_location = str(row["conservator_location"])
            if conservator_location.endswith("/"):
                # Remove trailing slash
                conservator_location = conservator_location[:-1]
            row["conservator_location"] = conservator_location.strip()

            default_metadata = default_metadata_dict.get(hardware_name)
            if default_metadata is None:
                stats.upload_entry_invalid_count += 1
                logger.warning(
                    f'Hardware named "{hardware_name}" could not be found (skipping entry). Please check {config_path}'
                )
                continue

            # guardian - for backwards compatibility (deprecated)
            if upload_type in [_UPLOAD_TYPE_PRISM, "guardian"]:
                uploader.upload_prism_capture(row, default_metadata, dry_run)
            elif upload_type == _UPLOAD_TYPE_VIDEO:
                uploader.upload_video_capture(
                    row, default_metadata, dry_run, camera_name_or_spectrum
                )
            elif upload_type == _UPLOAD_TYPE_IMAGES:
                uploader.upload_image_capture(
                    row, default_metadata, dry_run, camera_name_or_spectrum
                )
            else:
                logger.warning(
                    f'unsupported upload type "{upload_type}" (skipping)'
                )
                continue

    print(stats)

def main():
    """
    :return:
    :rtype:
    """

    parser = argparse.ArgumentParser(description="Batch upload videos to Conservator")

    parser.add_argument(
        "config",
        nargs="?",
        default=None,
        type=str,
        help="the name of the upload config (these correspond to folders in config/upload)",
    )

    parser.add_argument(
        "--dry_run", help="Set to false to upload to Conservator (true by default)"
    )

    parser.add_argument(
        "--config_root",
        help=f"Override where upload configurations are read \
            (defaults to {DEFAULT_UPLOAD_CONFIG_ROOT})",
    )
    # False by default...
    parser.add_argument("--debug", help="Turns on debug messages", action="store_true")

    args = parser.parse_args()

    if (args.dry_run is not None) and (args.dry_run.lower() == "false"):
        dry_run = False
    else:
        # Default is dry run mode
        dry_run = True

    if (
        args.config_root
        and isinstance(args.config_root, str)
        and len(args.config_root) > 0
    ):
        upload_config_root = args.config_root
    else:
        upload_config_root = DEFAULT_UPLOAD_CONFIG_ROOT

    if args.debug:
        _logger.setLevel(logging.DEBUG)

    main_helper(args, upload_config_root, _logger, dry_run)

    if dry_run:
        _logger.info("---------------------------------------------------------------------------")
        _logger.info(" NOTE: No data was uploaded. Set --dry_run=false to upload")
        _logger.info("---------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
