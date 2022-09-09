# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=super-init-not-called
# pylint: disable=unspecified-encoding
import collections
import multiprocessing
import subprocess
import os
import json
import shutil
import logging
import sys
import tempfile
import time
import functools
import requests
import jsonschema
import tqdm
from PIL import Image

from FLIR.conservator.file_transfers import FileDownloadException
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.util import md5sum_file, chunks
from FLIR.conservator.jsonl_to_index_json import jsonl_to_json
from FLIR.conservator.wrappers.dataset import Dataset

logger = logging.getLogger(__name__)


class InvalidLocalDatasetPath(Exception):
    def __init__(self, path):
        self.path = path


class LocalDataset:
    """
    Provides utilities for managing local datasets.

    This replicates the functionality of CVC, and should now be the
    preferred method of working with local datasets.

    :param conservator: A :class:`~FLIR.conservator.conservator.Conservator`
        instance to use for uploading new images.
    :param path: The path to the local dataset. This should point to the root
        directory (containing ``index.json`` and JSONL files).
    """

    TRACKED_FILES = ("index.json", "dataset.jsonl", "frames.jsonl", "videos.jsonl")
    WRITABLE_TRACKED_FILES = ("index.json", "dataset.jsonl", "frames.jsonl")

    def __init__(self, conservator, path):
        self.conservator = conservator
        self.path = os.path.abspath(path)
        self.index_path = os.path.join(self.path, "index.json")
        if not os.path.exists(self.index_path):
            raise InvalidLocalDatasetPath(self.path)
        # The following three paths may not exist depending on how long ago the
        # last dataset commit happened.  "frames.jsonl" and "videos.jsonl"
        # won't exist if there are no frames in the dataset.
        self.frames_path = os.path.join(self.path, "frames.jsonl")
        self.videos_path = os.path.join(self.path, "videos.jsonl")
        self.dataset_info_path = os.path.join(self.path, "dataset.jsonl")
        self.data_path = os.path.join(self.path, "data")
        self.analytics_path = os.path.join(self.path, "analyticsData")
        self.cvc_path = os.path.join(self.path, ".cvc")
        self.staging_path = os.path.join(self.cvc_path, ".staging.json")
        self.cache_path = conservator.config.cvc_cache_path

        if not os.path.isabs(self.cache_path):
            self.cache_path = os.path.join(self.path, self.cache_path)
        logger.debug("Using cache at %s", self.cache_path)

        if not os.path.exists(self.cvc_path):
            os.makedirs(self.cvc_path)
        if not os.path.exists(self.staging_path):
            with open(self.staging_path, "w+") as f:
                json.dump([], f)
        logger.debug("Opened local dataset at %s", self.path)

    def pull(self, verbose=True):
        """
        Pulls the latest repository state.

        :param verbose: If False, run git commands with the `-q` option.
        """
        fetch_cmd = ["git", "fetch"]
        if not verbose:
            fetch_cmd.append("-q")
        subprocess.call(fetch_cmd, cwd=self.path)
        checkout_cmd = ["git", "checkout", "origin/master", "-B", "master"]
        if not verbose:
            checkout_cmd.append("-q")
        return subprocess.call(checkout_cmd, cwd=self.path)

    def checkout(self, commit_hash, verbose=True):
        """
        Checks out a specific commit. This will delete any local changes in
        `index.json` or `associated_files`.

        :param verbose: If False, run git commands with the `-q` option.
        """
        checkout_cmd = ["git", "reset", "--hard"]
        if not verbose:
            checkout_cmd.append("-q")
        return subprocess.call(checkout_cmd + [commit_hash], cwd=self.path)

    def validate_jsonl(self):
        """
        Convert the contents of the .jsonl files into `index.json` format and
        validate the result.
        """
        jsonl_valid = True
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp_index:
            jsonl_to_json(self.path, tmp_index.name)
            jsonl_valid = self.validate_index(tmp_index.name)
        return jsonl_valid

    @staticmethod
    def get_jsonl_data(jsonl_file):
        """
        Create a single JSON list object from a JSONL source file.
        """
        data_array = []
        with open(jsonl_file, "r") as jsonl_f:
            for jsonl_line in jsonl_f:
                data_array.append(json.loads(jsonl_line))
        return data_array

    def write_frames_to_jsonl(self, frames_list):
        """
        Rewrite `frames.jsonl` with the contents of `frames_list`.
        """
        if not os.path.exists(self.dataset_info_path):
            logger.info("Skip write to frames.jsonl: Repository missing dataset.jsonl")
            return
        with open(self.frames_path, "w") as f:
            for frame in frames_list:
                f.write(f"{json.dumps(frame, separators=(',', ':'))}\n")

    def git_branch(self):
        """
        Return the git branch name for the dataset repository, if any.
        """
        branch_args = ["git", "branch"]
        branch_proc = subprocess.run(
            branch_args,
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            check=False,
        )
        if branch_proc.returncode != 0:
            logger.error("'%s' failed:\n%s", " ".join(branch_args), branch_proc.stdout)
            raise RuntimeError(f"`git branch` failed for {self.path}")

        branch_name = ""
        for bline in branch_proc.stdout.splitlines():
            if bline.startswith("*"):
                branch_name = bline[2:].rstrip()
        return branch_name

    def git_status(self):
        """
        Parse the git branch and status for the dataset repository.

        Returned table format:

        added -- contains a dictionary:

            * "staged" contains a list of new files that have been staged.
            * "working" contains a list of untracked files in the working
                directory.

        modified -- contains a dictionary:

            * "staged" contains a list of modified files that have been staged.
            * "working" contains a list of modified files in the working
                directory.

        other -- contains a list of dictionaries; for each dictionary in the
            list:

            * "index" contains the index status character (e.g. 'A', 'D', etc).
            * "working" contains the working directory status character.
            * "source" contains the file name associated with the status.
            * A rename or copy status will also contain a "dest" key.
        """
        status_table = {}
        status_args = ["git", "status", "--porcelain=v1"]
        status_proc = subprocess.run(
            status_args,
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        if status_proc.returncode != 0:
            logger.error("'%s' failed:\n%s", " ".join(status_args), status_proc.stderr)
            raise RuntimeError(f"`git status` failed for {self.path}")

        status_table["added"] = {"staged": [], "working": []}
        status_table["modified"] = {"staged": [], "working": []}
        status_table["other"] = []
        for status_line in status_proc.stdout.splitlines():
            index_stat = status_line[0]
            wdir_stat = status_line[1]
            if index_stat == "M":
                status_table["modified"]["staged"].append(status_line[3:])
            elif index_stat == "A":
                status_table["added"]["staged"].append(status_line[3:])
            if wdir_stat == "M":
                status_table["modified"]["working"].append(status_line[3:])
            elif wdir_stat == "?":
                status_table["added"]["working"].append(status_line[3:])
            if index_stat not in ("M", "A") and wdir_stat not in ("M", "?"):
                other_entry = {}
                if index_stat != " ":
                    other_entry["index"] = index_stat
                if wdir_stat != " ":
                    other_entry["working"] = wdir_stat
                operation = status_line[3:]
                if " -> " in operation:
                    entries = operation.split(" -> ")
                    other_entry["source"] = entries[0].strip()
                    other_entry["dest"] = entries[1].strip()
                else:
                    other_entry["source"] = operation
                status_table["other"].append(other_entry)
        return status_table

    def add_local_changes(self, skip_validation=False):
        """
        Stages changes to `index.json` or `*.jsonl` files and `associated_files` for the next commit.

        :param skip_validation: By default, `index.json` or `*.jsonl` are validated against a schema.
            If the schema is incorrect and you're sure your source files are valid, you can
            pass `True` to skip the check. In this case, please also submit a PR so we can
            update the schema.
        """
        if skip_validation:
            logger.warning(
                "Skipping validation. Please submit a PR if the schema should be changed."
            )

        branch_name = self.git_branch()
        if branch_name != "master":
            logger.warning(
                "Only the 'master' branch will accept changes.  Switch branches with \
                `git checkout master`."
            )
            return None

        repo_status = self.git_status()
        stage_files = []
        # Stage only files known to Conservator, or files in associated_files/.
        for modded in repo_status["modified"]["working"]:
            if modded == "videos.jsonl":
                logger.warning("Will not stage changes to read-only file '%s'.", modded)
            elif modded in self.WRITABLE_TRACKED_FILES:
                stage_files.append(modded)
            if os.path.dirname(modded) == "associated_files" and os.path.isfile(modded):
                stage_files.append(modded)
        jsonl_warning_printed = False
        for added in repo_status["added"]["working"]:
            if os.path.dirname(added) == "associated_files" and os.path.isfile(added):
                stage_files.append(added)
            if added.endswith(".jsonl") and added in self.WRITABLE_TRACKED_FILES:
                if added == "videos.jsonl":
                    logger.warning(
                        "Will not stage changes to read-only file '%s'.", added
                    )
                elif not os.path.exists(self.dataset_info_path):
                    if not jsonl_warning_printed:
                        logger.warning(
                            "'%s' cannot be added to a repository.  Move it aside, commit the current \
                            repository state from the Conservator web site and pull the new commit to \
                            get this file into the repository.",
                            added,
                        )
                    jsonl_warning_printed = True
                else:
                    stage_files.append(added)
        if not stage_files:
            logger.info(
                "No changes to be staged: no writable tracked files (%s) were modified, \
                and no new files were found in 'associated_files'.",
                ", ".join([f"'{afile}'" for afile in self.WRITABLE_TRACKED_FILES]),
            )
            return None

        jsonl_change = False
        for filename in stage_files:
            if not os.path.dirname(filename) and filename.endswith(".jsonl"):
                jsonl_change = True
                break
        if jsonl_change and "index.json" in stage_files:
            logger.error(
                "Cannot commit changes to index.json along with changes to any file ending in '.jsonl'"
            )
            logger.error(
                "Move JSONL and/or index.json files aside and recover the original versions using \
                `git restore <filename>`, then commit the conflicting changes separately."
            )
            sys.exit(-1)

        if not skip_validation:
            val_files = [
                valf for valf in stage_files if valf in self.WRITABLE_TRACKED_FILES
            ]
            if jsonl_change:
                val_ok = self.validate_jsonl()
            else:
                val_ok = self.validate_index()
            if not val_ok:
                logger.error(
                    "Not adding changes to %s. Doesn't match schema.",
                    ", ".join(val_files),
                )
                logger.error(
                    "You may be able to skip this check with '--skip-validation' if you're sure your file conforms."
                )
                sys.exit(-1)

        return subprocess.call(["git", "add"] + stage_files, cwd=self.path)

    def commit(self, message, verbose=True):
        """
        Commit added changes to the local git repo, with the given commit `message`.

        :param verbose: If False, run git commands with the `-q` option.
        """
        repo_status = self.git_status()
        # Verify whether there are any changes to the index.
        if not repo_status["modified"]["staged"] and not repo_status["added"]["staged"]:
            logger.warning("No changes staged, nothing to commit.")
            return None
        commit_cmd = ["git", "commit"]
        if not verbose:
            commit_cmd.append("-q")
        commit_cmd += ["-m", message]
        return subprocess.call(commit_cmd, cwd=self.path)

    def push_commits(self, verbose=True):
        """
        Push the git repo.

        :param verbose: If False, run git commands with the `-q` option.
        """
        # count existing commits to compare against later
        dataset = Dataset.from_local_path(self.conservator, self.path)
        num_initial_commits = len(dataset.get_commit_history())

        # The subprocess will return a non-zero exit code even if it succeeded.
        # Check its output to determine whether it worked.
        push_proc = subprocess.run(
            ["git", "push"],
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            check=False,
        )
        if "updated in conservator" not in push_proc.stdout:
            if "Everything up-to-date" in push_proc.stdout:
                logger.warning(push_proc.stdout)
            else:
                logger.error(
                    "Server did not accept changes to index.json:\n%s", push_proc.stdout
                )
                raise RuntimeError("Failed to push changes to index.json")

        # wait for another commit to appear
        found_new_commit = dataset.wait_for_history_len(num_initial_commits + 1)

        if found_new_commit:
            self.pull(verbose)
        else:
            logger.warning("Timeout waiting for commit to be processed on server")
            logger.warning(
                "Will need to run 'pull' later to get workdir synced with server"
            )

    def push_staged_images(self, copy_to_data=True, tries=5):
        """
        Push the staged images.

        This reads the staged image paths, uploads them, adds metadata
        to `index.json` (or `frames.jsonl` if it exists), and deletes the
        staged image paths.

        :param copy_to_data: If `True`, copy the staged images to the cache and
            link with the data directory. This produces the same result as
            downloading the images back from conservator (but without downloading).
        :param tries: Specify a retry limit when recovering from HTTP 502 errors.
        """
        image_paths = self.get_staged_images()
        if len(image_paths) == 0:
            logger.info("No files to push.")
            return

        branch_name = self.git_branch()
        if branch_name != "master":
            logger.warning(
                "Only the 'master' branch will accept image uploads.  Switch branches with \
                `git checkout master`."
            )
            return

        # Editing the `frames.jsonl` file is the preferred method.  For
        # datasets committed prior to JSONL support, fall back to editing
        # the `index.json` file.
        jsonl_update = True
        index = None
        dataset_info = self.get_dataset_info()
        if os.path.exists(self.dataset_info_path):
            dataset_frames = self.get_frames()
        else:
            jsonl_update = False
            index = self.get_index()
            dataset_frames = index.get("frames", [])
        next_index = LocalDataset.get_max_frame_index(dataset_frames) + 1

        video_id = dataset_info["datasetId"]

        image_chunks = chunks(image_paths, 100)

        for chunk in image_chunks:
            paths = list(filter(lambda path: path is not None, chunk))
            logger.debug("Processing next %s images...", len(paths))

            md5_list = []

            file_dict = {}

            for path in paths:
                image_info = LocalDataset.get_image_info(path)
                if image_info is None:
                    logger.error("Skipping '%s'", path)
                    continue
                md5_list.append(image_info["md5"])

                file_dict[image_info["md5"]] = image_info

            md5_check_result = self.conservator.query(
                Query.check_frames_by_md5, md5s=md5_list
            )

            for result in md5_check_result:

                logger.debug(result)

                image_data = file_dict[result.md5]

                if result.exists == "Invalid":
                    continue
                elif result.exists == "False":
                    logger.debug(
                        "File '%s' doesn't exist on conservator, uploading",
                        image_data["filename"],
                    )
                    self.upload_image(image_data["filename"], result.md5, tries=tries)
                else:
                    logger.debug(
                        "File '%s' already exists on conservator, skipping",
                        image_data["filename"],
                    )

                frame_id = self.conservator.generate_id()

                file_path = image_data["filename"]

                del image_data["filename"]

                new_frame = {
                    **image_data,
                    "datasetFrameId": frame_id,
                    "isEmpty": False,
                    "isFlagged": False,
                    "annotations": [],
                    "videoMetadata": {
                        "frameId": frame_id,
                        "videoId": video_id,
                        "frameIndex": next_index,
                    },
                }
                dataset_frames.append(new_frame)
                logger.debug("Added new DatasetFrame with id %s", frame_id)

                if copy_to_data:
                    os.makedirs(self.data_path, exist_ok=True)

                    # First copy it to the cache:
                    cache_path = self.get_cache_path(result.md5)
                    cache_dir = os.path.split(cache_path)[0]
                    os.makedirs(cache_dir, exist_ok=True)
                    logger.debug(
                        "Copying file from '%s' to '%s'", file_path, cache_path
                    )
                    shutil.copyfile(file_path, cache_path)

                    # Then link to data path:
                    filename = f"video-{video_id}-frame-{next_index:06d}-{frame_id}.jpg"
                    data_path = os.path.join(self.data_path, filename)
                    logger.debug("Linking '%s' to '%s'", data_path, cache_path)
                    os.link(cache_path, data_path)

                next_index += 1

        if jsonl_update:
            self.write_frames_to_jsonl(dataset_frames)
        else:
            with open(self.index_path, "w") as f:
                json.dump(index, f, indent=1, sort_keys=True, separators=(",", ": "))
        with open(self.staging_path, "w") as f:
            json.dump([], f)

    def upload_image(self, path, md5, tries=5):
        url = self.conservator.get_dvc_hash_url(md5)
        filename = os.path.split(path)[1]
        headers = {
            "Content-type": "image/jpeg",
            "x-amz-meta-originalfilename": filename,
        }
        logger.info("Uploading '%s'.", path)
        retry_count = 0
        while retry_count < tries:
            with open(path, "rb") as data:
                r = requests.put(url, data, headers=headers)
            if r.status_code == 502:
                retry_count += 1
                if retry_count < tries:
                    logger.info("Bad Gateway error, retrying %s..", filename)
                    time.sleep(retry_count)  # Timeout increases per retry.
                    continue
            else:
                break
        assert r.status_code == 200
        assert r.headers["ETag"] == f'"{md5}"'

    def get_index(self):
        """
        Returns the object in ``index.json``.
        """
        with open(self.index_path, "r") as f:
            return json.load(f)

    def get_frames(self):
        """
        Get the frames array for the dataset.

        Collect the data from `frames.jsonl` if present, else fall back to
        using the `index.json` file.
        """
        dataset_frames = []
        if os.path.exists(self.dataset_info_path):
            # An empty dataset won't have "frames.jsonl".
            if os.path.exists(self.frames_path):
                dataset_frames = LocalDataset.get_jsonl_data(self.frames_path)
        else:
            index = self.get_index()
            dataset_frames = index.get("frames", [])
        return dataset_frames

    def get_dataset_info(self):
        """
        Get the dataset's top-level info.

        Collect the data from `dataset.jsonl` if present, else fall back to
        using the `index.json` file.
        """
        dataset_info = {}
        if os.path.exists(self.dataset_info_path):
            with open(self.dataset_info_path) as ds_f:
                dataset_info = json.load(ds_f)
        else:
            index = self.get_index()
            for info_field in (
                "datasetId",
                "datasetName",
                "owner",
                "version",
                "overwrite",
            ):
                dataset_info[info_field] = index[info_field]
        return dataset_info

    def get_videos(self):
        """
        Get the videos array for the dataset.

        Collect the data from `videos.jsonl` if present, else fall back to
        using the `index.json` file.
        """
        videos = []
        if os.path.exists(self.videos_path):
            videos = LocalDataset.get_jsonl_data(self.videos_path)
        else:
            index = self.get_index()
            videos = index.get("videos", [])
        return videos

    def get_staged_images(self):
        """
        Returns the staged image paths from the staging file.
        """
        with open(self.staging_path, "r") as f:
            return json.load(f)

    def stage_local_images(self, image_paths):
        """
        Adds image paths to the staging file.
        """
        # First check all are valid paths
        for image_path in image_paths:
            if not os.path.exists(image_path):
                logger.error("Path '%s' does not exist.", image_path)
                return
            if os.path.isdir(image_path):
                logger.error("Path '%s' is a directory.", image_path)
                return
            if LocalDataset.get_image_info(image_path) is None:
                return

        # Then add absolute paths to staging file
        staged_images = self.get_staged_images()
        for image_path in image_paths:
            abspath = os.path.abspath(image_path)
            if abspath not in staged_images:
                logger.info("Adding '%s' to staging file.", abspath)
                staged_images.append(abspath)
        with open(self.staging_path, "w") as f:
            json.dump(staged_images, f)

    @staticmethod
    def get_image_info(path):
        """
        Returns image info to be added to a Dataset's ``index.json``, or `None`
        if there was an error.

        This opens the `path` using PIL to verify it is a JPEG image,
        and get the dimensions.
        """
        try:
            image = Image.open(path)
        except IOError:
            logger.error("'%s' is not an image", path)
            return

        if image.format != "JPEG":
            logger.error("'%s' is not a JPEG", path)
            return

        info = {
            "filename": path,
            "width": image.width,
            "height": image.height,
            "fileSize": os.path.getsize(path),
            "md5": md5sum_file(path),
        }
        return info

    @staticmethod
    def get_max_frame_index(dataset_frames):
        """
        Returns the maximum frame index in a dataset's frames.

        This only counts frames uploaded directly to the dataset.
        """
        max_index = 0
        for f in dataset_frames:
            if f["datasetFrameId"] == f["videoMetadata"]["frameId"]:
                frame_index = f["videoMetadata"]["frameIndex"]
                max_index = max(max_index, frame_index)
        return max_index

    def get_cache_path(self, md5):
        return os.path.join(self.cache_path, md5[:2], md5[2:])

    def clean_data_dir(self):
        for file in os.listdir(self.data_path):
            file_path = os.path.join(self.data_path, file)
            if os.path.islink(file_path) or os.stat(file_path).st_nlink > 1:
                os.remove(file_path)

    def _download_and_link(self, asset, max_retries=5):
        # we use imap (istarmap doesn't exist) so we need to unpack arguments
        try:
            download_path, url, paths_to_link, use_symlink = asset
            result = self.conservator.files.download(
                url=url,
                local_path=download_path,
                no_meter=True,
                max_retries=max_retries,
            )
            LocalDataset._add_links(download_path, paths_to_link, use_symlink)
            return result is not None and result.ok
        except FileDownloadException:
            return False

    @staticmethod
    def _add_links(path, paths_to_link, use_symlink):
        if not os.path.exists(path):
            return
        for link_path in paths_to_link:
            logger.debug("Linking '%s' to '%s'", link_path, path)
            if os.path.exists(link_path):
                os.remove(link_path)
            if use_symlink:
                os.symlink(path, link_path)
            else:
                os.link(path, link_path)

    def exists_in_cache(self, md5):
        cache_path = self.get_cache_path(md5)
        if not os.path.exists(cache_path):
            return False
        if not os.path.getsize(cache_path) > 0:
            logger.warning("Cache file '%s' was empty, ignoring.", cache_path)
            return False
        if not md5sum_file(cache_path) == md5:
            logger.warning("Cache file '%s' had invalid MD5, ignoring.", cache_path)
            return False
        return True

    def download(
        self,
        include_analytics=False,
        include_eight_bit=True,
        process_count=10,
        use_symlink=False,
        no_meter=False,
        tries=5,
    ):
        """
        Downloads the files listed in `frames.jsonl` or `index.json` of the
        local dataset.

        :param include_analytics: If `True`, download analytic data to
            `analyticsData/`.
        :param include_eight_bit: If `True`, download eight-bit images to
            `data/`.
        :param process_count: Number of concurrent download processes. Passing
            `None` will use `os.cpu_count()`.
        :param use_symlink: If `True`, use symbolic links instead of hardlinks
            when linking the cache and data.
        :param no_meter: If 'True', don't display file download progress
            meters.
        :param tries: Specify a retry limit when recovering from connection
            errors.
        """
        if include_eight_bit:
            os.makedirs(self.data_path, exist_ok=True)

        if include_analytics:
            os.makedirs(self.analytics_path, exist_ok=True)

        logger.info("Getting frames from frames.jsonl / index.json...")
        frame_count = 0
        # Stores unique keys in order of insertion. This maps hash -> [links]
        # dict is unordered until Python version 3.7+ (we support 3.6)
        hashes_required = collections.OrderedDict()
        for frame in self.get_frames():
            video_metadata = frame.get("videoMetadata", {})
            video_id = video_metadata.get("videoId", "")
            frame_index = video_metadata["frameIndex"]
            dataset_frame_id = frame["datasetFrameId"]
            if include_eight_bit:
                md5 = frame["md5"]
                name = (
                    f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.jpg"
                )
                path = os.path.join(self.data_path, name)

                hash_links = hashes_required.setdefault(md5, [])
                hash_links.append(path)
                frame_count += 1

            if include_analytics and ("analyticsMd5" in frame):
                md5 = frame["analyticsMd5"]
                name = (
                    f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.tiff"
                )
                path = os.path.join(self.analytics_path, name)

                hash_links = hashes_required.setdefault(md5, [])
                hash_links.append(path)
                frame_count += 1

        # If frames were deleted from frames.jsonl or index.json, we need to
        # clear them out of the data directory. Because we have the cache, we
        # can just delete everything.
        self.clean_data_dir()

        logger.info("Checking cache...")
        cache_hits = 0
        assets = []  # (path, name, url, paths_to_link, use_symlink)
        for md5, paths_to_link in hashes_required.items():
            cache_path = self.get_cache_path(md5)
            if self.exists_in_cache(md5):
                LocalDataset._add_links(cache_path, paths_to_link, use_symlink)
                cache_hits += 1
                logger.debug("Skipping %s: already downloaded.", md5)
                continue
            url = self.conservator.get_dvc_hash_url(md5)
            asset = (cache_path, url, paths_to_link, use_symlink)
            logger.debug("Going to download %s", md5)
            assets.append(asset)

        logger.info("Total frames: %s", frame_count)
        logger.info("  Unique hashes: %s", len(hashes_required))
        logger.info("  Already downloaded: %s", cache_hits)
        logger.info("  Missing: %s", len(assets))
        logger.info(
            "Going to download %s new frames using %s processes.",
            len(assets),
            process_count,
        )
        current_assets = list(assets)
        failures = 0
        results = []
        progress_msg = "Downloading new frames"
        for attempt in range(tries):
            with multiprocessing.Pool(process_count) as pool:
                download_method = functools.partial(
                    LocalDataset._download_and_link, self, max_retries=tries
                )
                progress = tqdm.tqdm(
                    iterable=pool.imap(download_method, current_assets),
                    desc=progress_msg,
                    total=len(current_assets),
                    disable=no_meter,
                )
                # We need to consume the results as they're output to update
                # the progress bar, we use list.
                results += list(progress)

            # We double check everything downloaded, and retry failures.
            failures = 0
            retry_assets = []
            for entry in current_assets:
                if not os.path.exists(entry[0]) or os.path.getsize(entry[0]) == 0:
                    if attempt < tries - 1:
                        logger.warning(
                            "Download to %s seems to have failed. Retrying ..",
                            entry[0],
                        )
                    else:
                        logger.error(
                            "Download to %s seems to have failed. Try again, or submit an issue.",
                            entry[0],
                        )
                    failures += 1
                    retry_assets.append(entry)
            if assets and failures >= len(assets):
                logger.error("All downloads failed!")
                break
            elif failures:
                current_assets = retry_assets
                progress_msg = "Retrying missing frames"
            else:
                break

        successes = len(assets) - failures

        logger.info("Downloads attempted: %s", len(assets))
        logger.info("  Reported %s successes.", sum(results))
        logger.info("  Successful downloads: %s", successes)
        logger.info("  Failed downloads: %s", failures)

        return failures == 0

    @staticmethod
    def clone(dataset, clone_path=None, verbose=True, max_retries=5, timeout=5):
        """Clone a `dataset` to a local path, returning a :class:`LocalDatasetOperations`.

        :param dataset: The dataset to clone. It must have a repository registered
            in Conservator.
        :param clone_path: The path where the git repo should be created. If `None`,
            the dataset is cloned into a subdirectory of the current path, using
            the Dataset's name.
        :param verbose: If False, run git commands with the `-q` option.
        :param max_retries: Retry this many times if the git clone command fails.
            This is intended to account for the race condition when a dataset has
            just been created using an API call and its repository is not
            immediately available.
        :param timeout: Delay this many seconds between retries.
        """
        dataset.populate(["name", "repository.master"])
        # Newly created datasets may not have a fully populated repository
        # right away, so allow for retries until the queued commits
        # produced by the server have finished.
        for _ in range(max_retries):
            if dataset.has_field("repository.master"):
                break
            logger.info(
                "Dataset %s not available for cloning, retry in %s seconds...",
                dataset.name,
                timeout,
            )
            time.sleep(timeout)
            dataset.populate(["name", "repository.master"])

        if not dataset.has_field("repository.master"):
            logging.error(
                "Dataset %s has no repository. Unable to clone.", dataset.name
            )
            logging.error(
                "This dataset can be fixed by browsing to it in Conservator Web UI and clicking 'Commit Changes'."
            )
            return

        if clone_path is None:
            clone_path = dataset.name

        if os.path.exists(clone_path):
            logging.error("Path %s already exists, can't clone.", clone_path)
            return

        url = dataset.get_git_url()
        clone_cmd = ["git", "clone"]
        if not verbose:
            clone_cmd.append("-q")
        clone_cmd += [url, clone_path]
        r = subprocess.call(clone_cmd)
        if r != 0:
            logging.error("Error %s when cloning.", r)
            return

        # pylint: disable=protected-access
        email = dataset._conservator.get_email()
        subprocess.call(["git", "config", "user.email", email], cwd=clone_path)

        # it's possible for the repository to exist, but for
        # the clone to go through before index.json has been downloaded.
        # this will cause the LocalDataset constructor to fail.
        # this re-pulls until index.json exists (or we timeout)
        index_path = os.path.join(clone_path, "index.json")
        for _ in range(max_retries):
            if os.path.exists(index_path):
                break
            time.sleep(timeout)
            subprocess.call(["git", "pull"], cwd=clone_path)
        else:
            # raise RuntimeError for compatibility with dataset-toolkit (see #165)
            raise RuntimeError("The repository exists, but does not contain index.json")
        # pylint: disable=protected-access
        return LocalDataset(dataset._conservator, clone_path)

    def validate_index(self, index_location=None):
        """
        Validates that the given ``index.json`` matches the expected JSON
        Schema.
        """
        schema_json = self.conservator.query(Query.validation_schema)
        schema = json.loads(schema_json)

        idx_location = index_location if index_location else self.index_path
        try:
            with open(idx_location) as index:
                index_data = json.load(index)
            jsonschema.validate(index_data, schema)
            return True
        except jsonschema.exceptions.ValidationError as validation_error:
            logger.error(validation_error.message)
            logger.debug(validation_error)
        return False
