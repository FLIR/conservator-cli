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
from utils.prism_capture import get_first_meta
from utils.config_reader import read_subfolder_config

import FLIR.conservator.conservator
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.wrappers import Video, Collection


# -------------------
#   Description
# -------------------
#  Upload data to Conservator

DEFAULT_UPLOAD_CONFIG_ROOT = osp.join(
    osp.dirname(osp.realpath(__file__)), "config", "upload"
)

os.environ["BASE_DIR"] = osp.dirname(osp.realpath(__file__))

# -------------------------------------
#               Logging
# -------------------------------------
_logger = logging.getLogger("upload")
_logger.setLevel(logging.INFO)
_ch = logging.StreamHandler()
# _ch.setFormatter(CustomFormatter())
_logger.addHandler(_ch)
FLIR.conservator.conservator.logger.setLevel(logging.DEBUG)

# -------------------------------------
#        Conservator CLI
# -------------------------------------
_conservator = Conservator.default()
_conservator: Conservator

# -------------------------------------
#               Stats
# -------------------------------------


class Stats:
    def __init__(self):
        self.upload_entry_count = 0
        self.upload_entry_commented_out_count = 0
        self.upload_entry_invalid_count = 0
        self.upload_video_count = 0
        self.would_upload_video_count = 0
        self.upload_metadata_count = 0
        self.video_still_processing_count = 0

    def __str__(self):
        string_table = PrettyTable(["Name", "Count"])
        string_table.align = "l"
        string_table.add_row(["Total entries", self.upload_entry_count])
        string_table.add_row(
            [
                "Total entries commented out by user",
                self.upload_entry_commented_out_count,
            ]
        )
        string_table.add_row(
            ["Total entries that are invalid", self.upload_entry_invalid_count]
        )
        string_table.add_row(
            ["Videos would be uploaded", self.would_upload_video_count]
        )
        string_table.add_row(["Videos ACTUALLY uploaded", self.upload_video_count])
        string_table.add_row(
            [
                "Videos currently being processed by Conservator",
                self.video_still_processing_count,
            ]
        )
        string_table.add_row(["Video metadata updated", self.upload_metadata_count])

        return str(string_table)


def _update_custom_video_helper(
    video_metadata: dict, existing_custom: dict, upload_custom: dict
) -> bool:
    """
    :param video_metadata: input and output (gets updated if changes are detected
    :param existing_custom:
    :param upload_custom:
    :return: True if updates were detection
    """
    has_updates = False
    # --------------------------------
    #     Update video source
    # --------------------------------
    existing_video_source = existing_custom.get("video_source")
    upload_video_source = upload_custom.get("video_source")

    if existing_video_source is None:
        video_metadata["custom"]["video_source"] = upload_video_source
        has_updates = True
    else:
        if existing_video_source.get("source_name") != upload_video_source.get(
            "source_name"
        ):
            video_metadata["custom"]["video_source"] = upload_video_source
            has_updates = True

    # --------------------------------
    #         Update RGBT
    # --------------------------------
    existing_destination = (
        existing_custom.get("rgbt", {}).get("rectify", {}).get("destination")
    )
    existing_apply_undistort = (
        existing_custom.get("rgbt", {}).get("rectify", {}).get("apply_undistort")
    )
    upload_rgbt = upload_custom.get("rgbt")
    if not isinstance(existing_destination, dict):
        video_metadata["custom"]["rgbt"] = upload_rgbt
        has_updates = True
    else:
        if upload_rgbt.get("rectify", {}).get("destination") is None:
            raise Exception("Invalid format for rectify")

        # This is not perfect, but typically the destination will be different on updates
        if (
            upload_rgbt["rectify"]["destination"]["point_tl"]
            != existing_destination["point_tl"]
            or upload_rgbt["rectify"]["destination"]["point_tr"]
            != existing_destination["point_tr"]
            or upload_rgbt["rectify"]["destination"]["point_bl"]
            != existing_destination["point_bl"]
            or upload_rgbt["rectify"]["destination"]["point_br"]
            != existing_destination["point_br"]
            or upload_rgbt["rectify"].get("apply_undistort") != existing_apply_undistort
        ):

            video_metadata["custom"]["rgbt"] = upload_rgbt
            has_updates = True

    return has_updates


def _update_string(key: str, data: dict, new_value: str) -> bool:
    if data.get(key, "") != new_value:
        if len(new_value):
            data[key] = new_value
        else:
            try:
                del data[key]
            except KeyError:
                pass
        _logger.debug("Metadata needs to be updated because of: %s", key)
        return True
    return False


def update_video_meta_data(
    video,
    video_metadata_all: dict,
    default_metadata: DefaultMetadata,
    specific_description: str,
    additional_tags: list,
    override_location: str,
    camera_name_or_spectrum: str,
    save_path: str,
    stats: Stats,
    dry_run: bool = True,
) -> bool:

    # ----------------------------------
    #     Preprocess Description
    # ----------------------------------
    new_description = specific_description
    generic_description = default_metadata.get_description(camera_name_or_spectrum)
    if len(generic_description):
        if len(new_description):
            new_description = new_description + ". " + generic_description
        else:
            new_description = generic_description

    # ----------------------------------
    #         Preprocess Tags
    # ----------------------------------
    new_tags = additional_tags
    generic_tags = default_metadata.get_tags(camera_name_or_spectrum)
    if len(generic_tags):
        new_tags = new_tags + generic_tags

    # ----------------------------------
    #        Preprocess Location
    # ----------------------------------
    new_location = default_metadata.get_location(camera_name_or_spectrum)
    if isinstance(override_location, str) and len(override_location) > 0:
        new_location = override_location

    # ----------------------------------
    #       Preprocess Spectrum
    # ----------------------------------
    if camera_name_or_spectrum == "thermal":
        conservator_spectrum = "Thermal"
    elif camera_name_or_spectrum == "rgb" or camera_name_or_spectrum == "visible":
        conservator_spectrum = "RGB"
    elif camera_name_or_spectrum == "mixed":
        conservator_spectrum = "Mixed"
    elif camera_name_or_spectrum == "other":
        conservator_spectrum = "Other"
    else:
        conservator_spectrum = "Unknown"

    # ----------------------------------
    #         Perform Updates
    # ----------------------------------
    # Assign by reference (video_metadata[] will modify video_metadata_all[])
    video_metadata = video_metadata_all["videos"][0]

    has_updates = False
    if _update_string("description", video_metadata, new_description):
        has_updates = True

    if _update_string("location", video_metadata, new_location):
        has_updates = True

    if _update_string("spectrum", video_metadata, conservator_spectrum):
        has_updates = True

    if video_metadata.get("tags", []) != new_tags:
        if len(new_tags):
            video_metadata["tags"] = new_tags
        else:
            try:
                del video_metadata["tags"]
            except KeyError:
                pass
        has_updates = True
        _logger.debug("       Metadata needs to be updated because of: tags")

    upload_custom = default_metadata.metadata[camera_name_or_spectrum].get("custom")
    if isinstance(upload_custom, dict):
        existing_custom = video_metadata.get("custom")

        if existing_custom is None:
            # Just copy the whole document
            has_updates = True
            video_metadata["custom"] = upload_custom
            _logger.debug("       Metadata needs to be updated because of: custom")
        else:
            # Selective update
            if _update_custom_video_helper(
                video_metadata, existing_custom, upload_custom
            ):
                has_updates = True
                _logger.debug("       Metadata needs to be updated because of: custom")

    if has_updates:
        with open(save_path, "w", encoding="UTF-8") as json_file:
            json.dump(
                video_metadata_all,
                json_file,
                sort_keys=False,
                indent=1,
                separators=(",", ": "),
            )

        if dry_run is False:
            video.upload_metadata(save_path)
            stats.upload_metadata_count += 1
            _logger.info("       Successfully updated video metadata")
    else:
        if dry_run is False:
            _logger.info("       Video does not require metadata updates")

    return has_updates


def upload_video_helper(local_path: str, remote_name: str, collection: Collection):
    """

    :param local_path: The local file path to upload.

    :param remote_name: If given, the remote name of the media. Otherwise, the local file
        name is used.

    :param collection: If specified, the Collection object, or `str` Collection ID to
        upload the media to

    :return: str of the video on success. None on failure
    """

    video_id = _conservator.videos.upload(
        local_path, collection=collection, remote_name=remote_name
    )
    if not video_id:
        _logger.error("Upload failed")

    # You can wait for processing in this manner (not required).
    # This script is designed to run multiples times
    # print("Waiting for processing")
    # _conservator.videos.wait_for_processing(video_id)
    return video_id


def get_video_and_collection(filename: str, conservator_location: str):

    video = None

    try:
        # Get collection
        collection = _conservator.collections.from_remote_path(
            conservator_location, make_if_no_exist=False, fields="id"
        )
    except FLIR.conservator.wrappers.collection.InvalidRemotePathException:
        collection = None

    if collection is not None:
        for video in collection.recursively_get_videos(
            fields=["name", "owner"], search_text=f'name:"{filename}"'
        ):
            if video.name == filename:
                video_url = _conservator.get_url() + "/videos/" + video.id
                _logger.info("Found %s/%s", conservator_location, filename)
                _logger.info("       URL: %s", video_url)
                return video, collection
    return video, collection


def upload_video(
    full_file_path: str,
    filename: str,
    collection: Collection,
    conservator_location: str,
) -> bool:
    """
    :param full_file_path: local path to the file to upload

    :param filename:

    :param collection: If specified, the Collection object, or `str` Collection ID to
        upload the media to

    :param conservator_location:
    :return:
    """
    if not osp.exists(full_file_path):
        print(f"File DOES NOT EXIST: {full_file_path}")
        return False

    try:
        _logger.info('Uploading "%s"', filename)
        _logger.info("   File on disk:         %s", full_file_path)
        _logger.info("   Conservator location: %s", conservator_location)

        video_id = upload_video_helper(full_file_path, filename, collection)
        video_url = _conservator.get_url() + "/videos/" + video_id

        _logger.info("   Success! See:         %s", video_url)
        return True
    except Exception as upload_error:
        _logger.error('Could not upload the file: "%s" (continuing)', filename)
        _logger.error(upload_error)
        return False


def check_if_expanded_properly(path: str) -> None:
    """
    Check to see if the expanded vars function mapped all the environment variables
    :param path:
    :return:
    """
    path_norm = os.path.normpath(path)
    path_parts = path_norm.split(os.sep)
    for path_part in path_parts:
        if len(path_part) == 0:
            continue

        if path_part[0] == "$":
            raise Exception(
                f"Error: could not expand environment variable {path_part}.\
                    Do you forget to set it? Try: export {path_part}=some_path"
            )


def still_processed_message():
    _logger.info("       Video is still being processed by Conservator")


def upload_video_capture(
    row: dict,
    default_metadata: DefaultMetadata,
    stats: Stats,
    dry_run: bool,
    camera_name_or_spectrum: str,
):
    """
    :param row:
    :param default_metadata:
    :param stats: keep track of stats to display to user
    :param dry_run: if False actually upload the Conservator
    :param camera_name_or_spectrum: identifies the specific default metadata
    :return:
    """
    local_path = osp.realpath(osp.expandvars(row["local_path"]))
    check_if_expanded_properly(local_path)

    if not osp.exists(local_path):
        raise Exception(f'The file could not be found: "{local_path}"')

    if not osp.isfile(local_path):
        raise Exception(
            f'For a video upload the "local_path" is expected to be a file.\
                The following is not a file: "{local_path}"'
        )

    head_tail = osp.split(local_path)
    path = head_tail[0]
    filename = head_tail[1]
    basename = osp.splitext(filename)[0]
    # The basename cannot be different
    meta_data_path = osp.join(path, f"{basename}.json")

    conservator_location = row["conservator_location"]

    # ---------------------------
    #     Upload Video file
    # ---------------------------
    video, collection = get_video_and_collection(filename, conservator_location)
    video_metadata = None

    if video is None:
        # Only if the file has not already been uploaded
        stats.would_upload_video_count += 1

        if dry_run is False:
            if collection is None:
                # We have not made the collection yet...
                # Create it recursively (this will create a project if it does not exist)
                collection = _conservator.collections.from_remote_path(
                    conservator_location, make_if_no_exist=True, fields="id"
                )

            upload_video(
                local_path,
                filename,
                collection=collection,
                conservator_location=conservator_location,
            )
            stats.upload_video_count += 1
        else:
            _logger.info("Video exists and is ready for upload: %s", local_path)
    else:
        if _conservator.videos.is_uploaded_media_id_processed(video.id):
            if dry_run is False:
                # When in dry run mode we only check location (no meta data)

                # Processing is done and we can not update the metadata
                video.download_metadata(osp.dirname(meta_data_path))
                _logger.info(
                    "       Downloading video metadata to temporary file: %s",
                    meta_data_path,
                )

                with open(meta_data_path, "r", encoding="UTF-8") as meta_data_file:
                    video_metadata = json.load(meta_data_file)
        else:
            stats.video_still_processing_count += 1
            still_processed_message()

    # -------------------------------
    #     Update Video Meta data
    # -------------------------------
    if video is not None and video_metadata is not None:
        update_video_meta_data(
            video,
            video_metadata,
            default_metadata,
            specific_description=row["description"],
            additional_tags=row["tags"],
            override_location=row.get("location", ""),
            camera_name_or_spectrum=camera_name_or_spectrum,
            save_path=meta_data_path,
            stats=stats,
            dry_run=dry_run,
        )

    # Newline for readability
    _logger.info("")


def upload_prism_capture(
    row: dict, default_metadata: DefaultMetadata, stats: Stats, dry_run: bool
):
    """
    :param row:
    :param default_metadata:
    :param stats: keep track of stats to display to user
    :param dry_run: if False actually upload the Conservator
    :return:
    """
    local_path = osp.realpath(osp.expandvars(row["local_path"]))
    check_if_expanded_properly(local_path)

    if not osp.exists(local_path):
        stats.upload_entry_invalid_count += 1
        _logger.warning(
            'The path "%s" could not be found (skipping entry). Please check your upload.csv file...',
            local_path,
        )
        return

    if not osp.isdir(local_path):
        stats.upload_entry_invalid_count += 1
        _logger.warning(
            'The path "%s" is not a directory (skipping entry). Please check your upload.csv file...',
            local_path,
        )
        return

    thermal_input_path = osp.join(local_path, "thermal")
    visible_input_path = osp.join(local_path, "visible")

    if not osp.exists(thermal_input_path) or not osp.isdir(thermal_input_path):
        stats.upload_entry_invalid_count += 1
        _logger.warning(
            'The path "%s" is not a directory or does not exist (skipping entry).\
                Please make sure this is a valid Prism recording...',
            thermal_input_path,
        )
        return

    if not osp.exists(visible_input_path) or not osp.isdir(visible_input_path):
        stats.upload_entry_invalid_count += 1
        _logger.warning(
            'The path "%s" is not a directory or does not exist (skipping entry).\
                Please make sure this is a valid Prism recording...',
            visible_input_path,
        )
        return

    upload_root_path = osp.realpath(osp.join(local_path, "", "upload"))

    if not osp.exists(upload_root_path):
        os.makedirs(upload_root_path, exist_ok=True)

    thermal_meta_path = osp.join(local_path, "thermal_meta")

    try:
        meta = get_first_meta(thermal_meta_path)
    except Exception as meta_error:
        stats.upload_entry_invalid_count += 1
        print(meta_error)
        _logger.warning(
            'Could not read the first thermal meta file at "%s" (skipping entry).\
                Please make sure this is a valid Prism recording...',
            thermal_meta_path,
        )
        return

    timestamp = str(meta["capture_timestamp_ms"])[0:10]  # Truncate

    conservator_location = row["conservator_location"]

    # ---------------------------
    #         Outputs
    # ---------------------------
    thermal_basename = f"{timestamp}_thermal"
    visible_basename = f"{timestamp}_visible"
    thermal_zip_filename = f"{thermal_basename}.zip"
    visible_zip_filename = f"{visible_basename}.zip"

    thermal_zip_path = osp.join(upload_root_path, thermal_zip_filename)
    visible_zip_path = osp.join(upload_root_path, visible_zip_filename)

    thermal_meta_data_path = osp.join(upload_root_path, f"{thermal_basename}.json")
    visible_meta_data_path = osp.join(upload_root_path, f"{visible_basename}.json")

    # ---------------------------------------
    #  Thermal: prepare zip files & upload
    # ---------------------------------------
    thermal_video, collection = get_video_and_collection(
        thermal_zip_filename, conservator_location
    )
    thermal_video_metadata = None
    if thermal_video is None:
        # Only if the file has NOT already been uploaded
        if dry_run:
            _logger.info(
                "Prism AI thermal exists and is ready for upload: %s",
                thermal_input_path,
            )

        stats.would_upload_video_count += 1
        if not osp.exists(thermal_zip_path):
            # Create the zip file if needed
            # (compress because these are typically 16-bit uncompressed tiffs)
            cmd = f"cd {upload_root_path} && zip -q -j\
                {thermal_zip_filename} {thermal_input_path}/*"
            _logger.info(
                "     Creating zip archive for upload: %s/%s",
                upload_root_path,
                thermal_zip_filename,
            )
            _logger.debug("     Zip command:")
            _logger.debug("         %s", cmd)
            os.system(cmd)

        if not dry_run:
            if collection is None:
                # We have not made the collection yet...
                # Create it recursively (this will create a project if it does not exist)
                collection = _conservator.collections.from_remote_path(
                    conservator_location, make_if_no_exist=True, fields="id"
                )

            upload_video(
                thermal_zip_path, thermal_zip_filename, collection, conservator_location
            )
            stats.upload_video_count += 1
    else:
        if _conservator.videos.is_uploaded_media_id_processed(thermal_video.id):

            if dry_run is False:
                # When in dry run mode we only check location (no meta data)

                # Processing is done and we can not update the metadata
                thermal_video.download_metadata(osp.dirname(thermal_meta_data_path))
                _logger.info(
                    "       Downloading video metadata to temporary file: %s",
                    thermal_meta_data_path,
                )

                with open(
                    thermal_meta_data_path, "r", encoding="UTF-8"
                ) as thermal_metadata:
                    thermal_video_metadata = json.load(thermal_metadata)
        else:
            stats.video_still_processing_count += 1
            still_processed_message()

    # ---------------------------------------
    #  Visible: prepare zip files & upload
    # ---------------------------------------
    visible_video, collection = get_video_and_collection(
        visible_zip_filename, conservator_location
    )
    visible_video_metadata = None
    if visible_video is None:
        # Only if the file has not already been uploaded
        if dry_run:
            _logger.info(
                "Prism AI visible exists and is ready for upload: %s",
                visible_input_path,
            )

        stats.would_upload_video_count += 1
        if not osp.exists(visible_zip_path):
            # Important: this command is slightly different than above: -0 means no compression
            cmd = f"cd {upload_root_path} && zip -0 -q -j\
                {visible_zip_filename} {visible_input_path}/*"
            _logger.info(
                "     Creating zip archive for upload: %s/%s",
                upload_root_path,
                visible_zip_filename,
            )
            _logger.debug("     Zip command:")
            _logger.debug("         %s", cmd)
            os.system(cmd)

        if not dry_run:
            if collection is None:
                # We have not made the collection yet...
                # Create it recursively (this will create a project if it does not exist)
                collection = _conservator.collections.from_remote_path(
                    conservator_location, make_if_no_exist=True, fields="id"
                )

            upload_video(
                visible_zip_path, visible_zip_filename, collection, conservator_location
            )
            stats.upload_video_count += 1
    else:
        if _conservator.videos.is_uploaded_media_id_processed(visible_video.id):

            if dry_run is False:
                # When in dry run mode we only check location (no meta data)

                # Processing is done and we can not update the metadata
                visible_video.download_metadata(osp.dirname(visible_meta_data_path))
                _logger.info(
                    "       Downloading video metadata to temporary file: %s",
                    visible_meta_data_path,
                )

                with open(
                    visible_meta_data_path, "r", encoding="UTF-8"
                ) as thermal_metadata:
                    visible_video_metadata = json.load(thermal_metadata)

        else:
            stats.video_still_processing_count += 1
            still_processed_message()

    # ---------------------------------------
    #     Joint Thermal <-> Visible data
    # ---------------------------------------
    if thermal_video_metadata is not None and visible_video_metadata is not None:
        if len(thermal_video_metadata["videos"][0]["frames"]) == len(
            visible_video_metadata["videos"][0]["frames"]
        ):
            for i, thermal_frame in enumerate(
                thermal_video_metadata["videos"][0]["frames"]
            ):
                visible_frame = visible_video_metadata["videos"][0]["frames"][i]

                # Make frame references
                thermal_frame["associatedFrames"] = [
                    {"spectrum": "RGB", "frameId": visible_frame["frameId"]}
                ]

                visible_frame["associatedFrames"] = [
                    {"spectrum": "Thermal", "frameId": thermal_frame["frameId"]}
                ]
        else:
            _logger.warning(
                "visible / thermal frames do not have matching counts (not adding visible <-> thermal frame mapping)"
            )

        # -------------------------------
        #     Update Video Meta Data
        # -------------------------------
        update_video_meta_data(
            visible_video,
            visible_video_metadata,
            default_metadata,
            specific_description=row["description"],
            additional_tags=row["tags"],
            override_location=row.get("location", ""),
            camera_name_or_spectrum="rgb",
            save_path=visible_meta_data_path,
            stats=stats,
            dry_run=dry_run,
        )

        update_video_meta_data(
            thermal_video,
            thermal_video_metadata,
            default_metadata,
            specific_description=row["description"],
            additional_tags=row["tags"],
            override_location=row.get("location", ""),
            camera_name_or_spectrum="thermal",
            save_path=thermal_meta_data_path,
            stats=stats,
            dry_run=dry_run,
        )

    # Newline for readability
    _logger.info("")


def show_help(default_config_path: str, config_filename: str) -> None:
    """
    :param default_config_path: root path to configs
    :param config_filename:
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
            config_data = json.load(config_file)
            help_table.add_row([config_folder, config_data.get("description", "")])
    print(help_table)
    sys.exit(1)


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

    config_filename = "upload.json"
    config_path = read_subfolder_config(
        args, upload_config_root, config_filename, show_help=show_help
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
        _logger.fatal(
            "missing upload list CSV file. Expected it here: %s",
            upload_list_path,
        )
        sys.exit(1)

    stats = Stats()

    with open(upload_list_path, encoding="UTF-8") as list_data_file:
        reader = csv.DictReader(list_data_file)

        for row in reader:
            stats.upload_entry_count += 1
            upload_type = str(row["type"]).lower()

            if len(upload_type) > 0 and upload_type[0] == "#":
                stats.upload_entry_commented_out_count += 1
                continue

            hardware_name = str(row["hardware_name"]).lower()
            camera_name_or_spectrum = None
            if upload_type == "video":
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
                _logger.warning(
                    'Hardware named "%s" could not be found (skipping entry). Please check %s',
                    hardware_name,
                    config_path,
                )
                continue

            if (
                upload_type == "prism" or upload_type == "guardian"
            ):  # For backwards compatibility
                upload_prism_capture(row, default_metadata, stats, dry_run)
            elif upload_type == "video":
                upload_video_capture(
                    row, default_metadata, stats, dry_run, camera_name_or_spectrum
                )
            else:
                _logger.warning(
                    'unsupported upload type "%s" (skipping)',
                    upload_type,
                )
                continue

    print(stats)

    if dry_run:
        print(
            "---------------------------------------------------------------------------"
        )
        print(" NOTE: No data was uploaded. Set --dry_run=false to upload")
        print(
            "---------------------------------------------------------------------------"
        )


if __name__ == "__main__":
    main()
