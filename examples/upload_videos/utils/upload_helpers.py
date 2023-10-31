import json
import logging
import os
from os import path as osp

from prettytable import PrettyTable

import FLIR.conservator
from FLIR.conservator.wrappers import Collection, Video
from FLIR.conservator.conservator import Conservator

from .default_metadata import DefaultMetadata
from .prism_capture import get_first_meta

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

class Uploader:

    def __init__(self, logger: logging.Logger, conservator: Conservator, stats: Stats):
        self._logger = logger
        self._conservator = conservator
        self._stats = stats

    def upload_video(
        self,
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
            self._logger.error(f"File DOES NOT EXIST: {full_file_path}")
            return False

        try:
            self._logger.info(f'Uploading "{filename}"', )
            self._logger.info(f"   File on disk:         {full_file_path}", )
            self._logger.info(f"   Conservator location: {conservator_location}", )

            video_id = self.upload_video_helper(full_file_path, filename, collection)
            video_url = self._conservator.get_url() + "/videos/" + video_id

            self._logger.info(f"   Success! See:         {video_url}", )
            return True
        except Exception as upload_error:
            self._logger.error(f'Could not upload the file: "{filename}" (continuing)')
            self._logger.error(upload_error)
            return False

    def _update_string(self, key: str, data: dict, new_value: str) -> bool:
        if data.get(key, "") != new_value:
            if len(new_value):
                data[key] = new_value
            else:
                try:
                    del data[key]
                except KeyError:
                    pass
            self._logger.debug(f'Metadata needs to be updated because of: "{key}"')
            return True
        return False

    def update_video_meta_data(
        self,
        video,
        video_metadata_all: dict,
        default_metadata: DefaultMetadata,
        specific_description: str,
        additional_tags: list,
        override_location: str,
        camera_name_or_spectrum: str,
        save_path: str,
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
        # Prefer the explicitly provided spectrum
        conservator_spectrum = 'Unknown'
        try:
            conservator_spectrum = self.get_conservator_spectrum(default_metadata.get_spectrum(camera_name_or_spectrum))
        except Exception as e:
            logging.warning(e)

        if conservator_spectrum == 'Unknown':
            # Revert to the camera "name"
            conservator_spectrum = self.get_conservator_spectrum(camera_name_or_spectrum)

        # ----------------------------------
        #         Perform Updates
        # ----------------------------------
        # Assign by reference (video_metadata[] will modify video_metadata_all[])
        video_metadata = video_metadata_all["videos"][0]

        has_updates = False
        if self._update_string("description", video_metadata, new_description):
            has_updates = True

        if self._update_string("location", video_metadata, new_location):
            has_updates = True

        if self._update_string("spectrum", video_metadata, conservator_spectrum):
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
            self._logger.debug("       Metadata needs to be updated because of: tags")

        upload_custom = default_metadata.metadata[camera_name_or_spectrum].get("custom")
        if isinstance(upload_custom, dict):
            existing_custom = video_metadata.get("custom")

            if existing_custom is None:
                # Just copy the whole document
                has_updates = True
                video_metadata["custom"] = upload_custom
                self._logger.debug("       Metadata needs to be updated because of: custom")
            else:
                # Selective update
                if self._update_custom_video_helper(
                    video_metadata, existing_custom, upload_custom
                ):
                    has_updates = True
                    self._logger.debug("       Metadata needs to be updated because of: custom")

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
                self._stats.upload_metadata_count += 1
                self._logger.info("       Successfully updated video metadata")
        else:
            if dry_run is False:
                self._logger.info("       Video does not require metadata updates")

        return has_updates

    def upload_video_helper(self, local_path: str, remote_name: str, collection: Collection):
        """

        :param local_path: The local file path to upload.

        :param remote_name: If given, the remote name of the media. Otherwise, the local file
            name is used.

        :param collection: If specified, the Collection object, or `str` Collection ID to
            upload the media to

        :return: str of the video on success. None on failure
        """

        video_id = self._conservator.videos.upload(
            local_path, collection=collection, remote_name=remote_name
        )

        if not video_id:
            self._logger.error("Upload failed")

        # You can wait for processing in this manner (not required).
        # This script is designed to run multiples times to let Conservator process the upload.
        # Afterward metadata is updated.
        # print("Waiting for processing")
        # _conservator.videos.wait_for_processing(video_id)
        return video_id

    def get_video_and_collection(self, filename: str, conservator_location: str):
        video = None

        try:
            # Get collection
            collection = self._conservator.collections.from_remote_path(
                conservator_location, make_if_no_exist=False, fields="id"
            )
        except FLIR.conservator.wrappers.collection.InvalidRemotePathException:
            collection = None

        if collection is not None:
            for video in collection.recursively_get_videos(
                fields=["name", "owner"], search_text=f'name:"{filename}"'
            ):
                if video.name == filename:
                    video_url = self._conservator.get_url() + "/videos/" + video.id
                    self._logger.info(f"Found {conservator_location}/{filename}")
                    self._logger.info(f"       URL: {video_url}")
                    return video, collection
        return video, collection

    def still_processed_message(self):
        self._logger.info("       Video is still being processed by Conservator")

    def get_metadata_if_ready(self, video: Video, metadata_path: str, dry_run: bool) -> object:
        """
        :param video: Conservator video object
        :param metadata_path: path to save video metadata (Conservator CLI must download first)
        :param dry_run: true - metadata will actually be downloaded,
                        false - only display message if video is still processing
        :return: None if metadata was not downloaded
                 dict of metadata file (if metadata was downloaded successfully)
        """
        video_metadata = None
        if self._conservator.videos.is_uploaded_media_id_processed(video.id):
            if dry_run is False:
                # Processing is done and we can update the metadata
                video.download_metadata(osp.dirname(metadata_path))
                self._logger.info(
                    f"       Downloading video metadata to temporary file: {metadata_path}"
                )

                with open(metadata_path, "r", encoding="UTF-8") as meta_data_file:
                    video_metadata = json.load(meta_data_file)
        else:
            self._stats.video_still_processing_count += 1
            self.still_processed_message()

        return video_metadata

    def upload_video_capture(
        self,
        row: dict,
        default_metadata: DefaultMetadata,
        dry_run: bool,
        camera_name_or_spectrum: str,
    ):
        """
        :param row:
        :param default_metadata:
        :param dry_run: if False actually upload the Conservator
        :param camera_name_or_spectrum: identifies the specific default metadata
        :return:
        """
        local_path = osp.realpath(osp.expandvars(row["local_path"]))
        self.check_if_expanded_properly(local_path)

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
        video, collection = self.get_video_and_collection(filename, conservator_location)
        video_metadata = None

        if video is None:
            # Only if the file has not already been uploaded
            self._stats.would_upload_video_count += 1

            if dry_run is False:
                if collection is None:
                    # We have not made the collection yet...
                    # Create it recursively (this will create a project if it does not exist)
                    collection = self._conservator.collections.from_remote_path(
                        conservator_location, make_if_no_exist=True, fields="id"
                    )

                self.upload_video(
                    local_path,
                    filename,
                    collection=collection,
                    conservator_location=conservator_location,
                )
                self._stats.upload_video_count += 1
            else:
                self._logger.info(f"Video exists and is ready for upload: {local_path}")
        else:
            # Conservator has a record of the upload - has processing completed? If so get the metadata.
            video_metadata = self.get_metadata_if_ready(video, meta_data_path, dry_run)

        # -------------------------------
        #     Update Video Meta data
        # -------------------------------
        if video is not None and video_metadata is not None:
            self.update_video_meta_data(
                video,
                video_metadata,
                default_metadata,
                specific_description=row["description"],
                additional_tags=row["tags"],
                override_location=row.get("location", ""),
                camera_name_or_spectrum=camera_name_or_spectrum,
                save_path=meta_data_path,
                dry_run=dry_run,
            )

        # Newline for readability
        self._logger.info("")

    def upload_prism_capture(
        self, row: dict, default_metadata: DefaultMetadata, dry_run: bool
    ):
        """
        :param row:
        :param default_metadata:
        :param dry_run: if False actually upload the Conservator
        :return:
        """
        local_path = osp.realpath(osp.expandvars(row["local_path"]))
        self.check_if_expanded_properly(local_path)

        if not self.local_path_passes_sanity_checks(local_path):
            return

        upload_root_path = osp.realpath(osp.join(local_path, "upload"))
        if not dry_run:
            os.makedirs(upload_root_path, exist_ok=True)

        thermal_input_path = osp.join(local_path, "thermal")
        visible_input_path = osp.join(local_path, "visible")

        if not osp.exists(thermal_input_path) or not osp.isdir(thermal_input_path):
            self._stats.upload_entry_invalid_count += 1
            self._logger.warning(
                f'The path "{thermal_input_path}" is not a directory or does not exist (skipping entry).\
                    Please make sure this is a valid Prism recording...'
            )
            return

        if not osp.exists(visible_input_path) or not osp.isdir(visible_input_path):
            self._stats.upload_entry_invalid_count += 1
            self._logger.warning(
                f'The path "{visible_input_path}" is not a directory or does not exist (skipping entry).\
                    Please make sure this is a valid Prism recording...'
            )
            return

        thermal_meta_path = osp.join(local_path, "thermal_meta")

        try:
            meta = get_first_meta(thermal_meta_path)
        except Exception:
            self._stats.upload_entry_invalid_count += 1

            self._logger.warning(
                f'Could not read the first thermal meta file at "{thermal_meta_path}" (skipping entry).\
                    Please make sure this is a valid Prism recording...'
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
        thermal_video, collection = self.get_video_and_collection(
            thermal_zip_filename, conservator_location
        )
        thermal_video_metadata = None
        if thermal_video is None:
            # Only if the file has NOT already been uploaded
            if dry_run:
                self._logger.info(f"Prism AI thermal exists and is ready for upload: {thermal_input_path}")

            self._stats.would_upload_video_count += 1
            if not osp.exists(thermal_zip_path):
                # Create the zip file if needed
                # (compress because these are typically 16-bit uncompressed tiffs)
                # Use -r rather than /* to avoid getting "zip: Argument list too long"
                cmd = f"cd {thermal_input_path} && zip -q -j -r {thermal_zip_path} ."

                self._logger.info(
                    f"     Creating zip archive for upload: {thermal_basename}"
                )
                self._logger.debug("     Zip command:")
                self._logger.debug(f"         {cmd}")
                os.system(cmd)

            if not dry_run:
                if collection is None:
                    # We have not made the collection yet...
                    # Create it recursively (this will create a project if it does not exist)
                    collection = self._conservator.collections.from_remote_path(
                        conservator_location, make_if_no_exist=True, fields="id"
                    )

                self.upload_video(
                    thermal_zip_path, thermal_zip_filename, collection, conservator_location
                )
                self._stats.upload_video_count += 1
        else:
            # Conservator has a record of the upload - has processing completed? If so get the metadata.
            thermal_video_metadata = self.get_metadata_if_ready(thermal_video, thermal_meta_data_path, dry_run)

        # ---------------------------------------
        #  Visible: prepare zip files & upload
        # ---------------------------------------
        visible_video, collection = self.get_video_and_collection(
            visible_zip_filename, conservator_location
        )
        visible_video_metadata = None
        if visible_video is None:
            # Only if the file has not already been uploaded
            if dry_run:
                self._logger.info(f"Prism AI visible exists and is ready for upload: {visible_input_path}")

            self._stats.would_upload_video_count += 1
            if not osp.exists(visible_zip_path):
                # Important: this command is slightly different from above: -0 means no compression
                # Use -r rather than /* to avoid getting "zip: Argument list too long"
                cmd = f"cd {visible_input_path} && zip -0 -q -j -r {visible_zip_path} ."

                self._logger.info(
                    f"     Creating zip archive for upload: {visible_basename}"
                )
                self._logger.debug("     Zip command:")
                self._logger.debug(f"           {cmd}")
                os.system(cmd)

            if not dry_run:
                if collection is None:
                    # We have not made the collection yet...
                    # Create it recursively (this will create a project if it does not exist)
                    collection = self._conservator.collections.from_remote_path(
                        conservator_location, make_if_no_exist=True, fields="id"
                    )

                self.upload_video(
                    visible_zip_path, visible_zip_filename, collection, conservator_location
                )
                self._stats.upload_video_count += 1
        else:
            # Conservator has a record of the upload - has processing completed? If so get the metadata.
            visible_video_metadata = self.get_metadata_if_ready(visible_video, visible_meta_data_path, dry_run)

        # ---------------------------------------
        #     Joint Thermal <-> Visible data
        # ---------------------------------------
        if type(thermal_video_metadata) is dict and type(visible_video_metadata) is dict:
            thermal_video_metadata: dict
            visible_video_metadata: dict
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
                self._logger.warning(
                    "visible / thermal frames do not have matching counts (not adding visible <-> thermal frame mapping)"
                )

            # -------------------------------
            #     Update Video Meta Data
            # -------------------------------
            self.update_video_meta_data(
                visible_video,
                visible_video_metadata,
                default_metadata,
                specific_description=row["description"],
                additional_tags=row["tags"],
                override_location=row.get("location", ""),
                camera_name_or_spectrum="rgb",
                save_path=visible_meta_data_path,
                dry_run=dry_run,
            )

            self.update_video_meta_data(
                thermal_video,
                thermal_video_metadata,
                default_metadata,
                specific_description=row["description"],
                additional_tags=row["tags"],
                override_location=row.get("location", ""),
                camera_name_or_spectrum="thermal",
                save_path=thermal_meta_data_path,
                dry_run=dry_run,
            )

        # Newline for readability
        self._logger.info("")

    def upload_image_capture(
        self, row: dict, default_metadata: DefaultMetadata, dry_run: bool, camera_name_or_spectrum: str
    ):
        """
        :param row:
        :param default_metadata:
        :param dry_run: if False actually upload the Conservator
        :param camera_name_or_spectrum: identifies the specific default metadata
        :return:
        """
        local_path = osp.realpath(osp.expandvars(row["local_path"]))
        self.check_if_expanded_properly(local_path)

        if not self.local_path_passes_sanity_checks(local_path):
            return

        upload_root_path = osp.realpath(osp.join(local_path, "..", "upload"))
        if not dry_run:
            os.makedirs(upload_root_path, exist_ok=True)

        conservator_location = row["conservator_location"]
        basename = osp.basename(local_path)
        zip_filename = f"{basename}.zip"
        zip_path = osp.join(upload_root_path, zip_filename)

        metadata_path = osp.join(upload_root_path, f"{basename}.json")

        # ---------------------------------------
        #      prepare zip files & upload
        # ---------------------------------------
        video, collection = self.get_video_and_collection(
            zip_filename, conservator_location
        )

        video_metadata = None
        if video is None:
            self._stats.would_upload_video_count += 1
            if not osp.exists(zip_path):
                # Create the zip file if needed
                # (compress because these are typically 16-bit uncompressed tiffs)
                # Use -r rather than /* to avoid getting "zip: Argument list too long"
                cmd = f"cd {local_path} && zip -q -j -r {zip_path} ."

                if dry_run:
                    self._logger.info(f"     Would run: {cmd}")
                else:
                    self._logger.info(
                        f"     Creating zip archive for upload: {upload_root_path}/{zip_filename}"
                    )
                    self._logger.debug("     Zip command:")
                    self._logger.debug(f"         {cmd}", )
                    os.system(cmd)
            else:
                if dry_run:
                    self._logger.info(f"Image exists and is ready for upload: {zip_path}")

            if not dry_run:
                if collection is None:
                    # We have not made the collection yet...
                    # Create it recursively (this will create a project if it does not exist)
                    collection = self._conservator.collections.from_remote_path(
                        conservator_location, make_if_no_exist=True, fields="id"
                    )

                self.upload_video(
                    zip_path, zip_filename, collection, conservator_location
                )
                self._stats.upload_video_count += 1
        else:
            # Conservator has a record of the upload - has processing completed? If so get the metadata.
            video_metadata = self.get_metadata_if_ready(video, metadata_path, dry_run)

        if type(video_metadata) is dict:
            # Dry run flag is checked inside
            self.update_video_meta_data(
                video,
                video_metadata,
                default_metadata,
                specific_description=row["description"],
                additional_tags=row["tags"],
                override_location=row.get("location", ""),
                camera_name_or_spectrum=camera_name_or_spectrum,
                save_path=metadata_path,
                dry_run=dry_run,
            )

        # Newline for readability
        self._logger.info("")

    def local_path_passes_sanity_checks(self, local_path: str):
        if not osp.exists(local_path):
            self._stats.upload_entry_invalid_count += 1
            self._logger.warning(
                f'The path "{local_path}" could not be found (skipping entry). Please check your upload.csv file...'
            )
            return False

        if not osp.isdir(local_path):
            self._stats.upload_entry_invalid_count += 1
            self._logger.warning(
                f'The path "{local_path}" is not a directory (skipping entry). Please check your upload.csv file...'
            )
            return False
        return True

    @staticmethod
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

    @staticmethod
    def get_conservator_spectrum(value: str):
        value_lower = value.lower()
        if value_lower == "thermal":
            return "Thermal"
        elif value_lower == "rgb" or value_lower == "visible":
            return "RGB"
        elif value_lower == "mixed":
            return "Mixed"
        elif value_lower == "other":
            return "Other"

        return "Unknown"

    @staticmethod
    def _update_custom_video_helper(video_metadata: dict, existing_custom: dict, upload_custom: dict) -> bool:
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
