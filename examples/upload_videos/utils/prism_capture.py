# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=broad-except
import json
import os
from os import path as osp


def get_meta_files(dir_root_path):
    files = os.listdir(dir_root_path)
    return sorted(files)


def get_first_meta(dir_root_path: str):
    """
    :param dir_root_path:
    :return:
    """
    files = get_meta_files(dir_root_path)
    for filename in files:
        ext = osp.splitext(filename)[1]

        ext = ext.lower()

        if ext != ".json":
            continue

        file_path = osp.join(dir_root_path, filename)

        with open(file_path, "r", encoding="UTF-8") as file:
            return json.load(file)


def get_meta(
    dir_root_path: str,
    squash_time_diff: bool = True,
    id_start: int = -1,
    id_end: int = -1,
    exit_on_failure: bool = True,
    quiet: bool = False,
) -> list:
    """
    :param dir_root_path:
    :param squash_time_diff:
    :param id_start: [optional] start at a frame index for efficiency
    :param id_end: [optional] end at a frame index for efficiency
    :param exit_on_failure: exit if there is a failure parsing the dataset (True by default)
    :param quiet:

    :return:
    :rtype: list
    """
    files = get_meta_files(dir_root_path)
    meta = []
    small_time_gap = 200
    big_time_gap = 1000

    if not quiet:
        print(f"  Found {len(files):,} total meta files in {dir_root_path}")

    for filename in files:
        basename, ext = osp.splitext(filename)

        ext = ext.lower()

        if ext != ".json":
            continue

        meta_id = int(basename)

        if id_start > -1:
            if meta_id < id_start:
                continue

        if id_end > -1:
            if meta_id > id_end:
                continue

        try:
            # Sanity check...
            file_path = osp.join(dir_root_path, filename)

            with open(file_path, "r", encoding="UTF-8") as metadata_file:
                current_meta = json.load(metadata_file)

            current_time = int(current_meta["capture_relative_ms"])

            if squash_time_diff is True:
                meta_len = len(meta)
                if meta_len == 0:
                    current_meta["capture_relative_ms_adjusted"] = current_time
                    meta.append(current_meta)
                    continue

                # We have a last time
                last_time = int(meta[meta_len - 1]["capture_relative_ms"])
                last_adjusted_time = int(
                    meta[meta_len - 1]["capture_relative_ms_adjusted"]
                )

                time_delta = current_time - last_time

                if time_delta >= small_time_gap or time_delta < 0:
                    # There is a big time gap between frames.
                    # It could be that some footage was manually cut out
                    # or we are putting together multiple recordings for a demo
                    if time_delta >= big_time_gap:
                        # These are likely two different clips...
                        # Force a negative time change so that
                        # predictions are cleared (looks better for demos)
                        adjust_ms = -1000
                    else:
                        # Likely: shutter was activated and it caused a delay,
                        # simply remove delay by putting in a fairly small time delta
                        adjust_ms = 25
                else:
                    adjust_ms = time_delta

                current_meta["capture_relative_ms_adjusted"] = (
                    last_adjusted_time + adjust_ms
                )
            else:
                # Don't adjust time...
                current_meta["capture_relative_ms_adjusted"] = current_time

            meta.append(current_meta)

            if not quiet:
                meta_count = len(meta)
                if meta_count % 500 == 0:
                    print(f"  Read {meta_count:,} meta files")
        except Exception as metadata_error:
            print(f"Failed at file: {osp.join(dir_root_path, filename)}")
            print(metadata_error)
            if exit_on_failure:
                print("Exiting due to failure...")
                exit(1)
            else:
                print("Ignoring failure and continuing")
    return meta


def check_dir(path):
    """
    Check if path exists and is a directory

    :param path: path to expected directory
    :type path: str
    :return: None
    :rtype: None
    """
    if not osp.exists(path):
        raise Exception(f"Expected paths does not exist: {path}")

    if not osp.isdir(path):
        raise Exception(f"Path is not a directory: {path}")


def get_files_with_ext(dir_root_path: str, match_ext, image_prefix: str) -> list:
    """
    :param dir_root_path:
    :param match_ext:
    :type match_ext: str or list
    :param image_prefix:

    :return:
    :rtype: list
    """
    files = os.listdir(dir_root_path)
    files = sorted(files)
    matching_files = []
    if isinstance(match_ext, str):
        match_ext = [match_ext]

    print(f"Found {len(files)} total files in the {image_prefix} directory")

    for file in files:
        file_path = osp.join(dir_root_path, file)
        if osp.isdir(file_path):
            # Shouldn't happen, but just in case...
            continue

        splitext = osp.splitext(file)
        if len(splitext) != 2:
            continue

        ext = splitext[1].lower()

        if ext not in match_ext:
            continue

        # We store a shorter path that is not absolute.
        # The json file will store the prefix to prepend
        short_path = osp.join(image_prefix, file)
        matching_files.append(short_path)
        matching_count = len(matching_files)
        if matching_count % 500 == 0:
            print(f"  Found {matching_count:,} {image_prefix} image files")

    return matching_files
