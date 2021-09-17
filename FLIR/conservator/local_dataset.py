import collections
import multiprocessing
import subprocess
import os
import json
import shutil
import requests
import logging
import time
import functools

import jsonschema
import tqdm
from PIL import Image

from FLIR.conservator.file_transfers import FileDownloadException
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.util import md5sum_file

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
        directory (containing ``index.json``).
    """

    def __init__(self, conservator, path):
        self.conservator = conservator
        self.path = os.path.abspath(path)
        self.index_path = os.path.join(self.path, "index.json")
        if not os.path.exists(self.index_path):
            raise InvalidLocalDatasetPath(self.path)
        self.data_path = os.path.join(self.path, "data")
        self.analytics_path = os.path.join(self.path, "analyticsData")
        self.cvc_path = os.path.join(self.path, ".cvc")
        self.staging_path = os.path.join(self.cvc_path, ".staging.json")
        self.cache_path = conservator.config.cvc_cache_path

        if not os.path.isabs(self.cache_path):
            self.cache_path = os.path.join(self.path, self.cache_path)
        logger.debug(f"Using cache at {self.cache_path}")

        if not os.path.exists(self.cvc_path):
            os.makedirs(self.cvc_path)
        if not os.path.exists(self.staging_path):
            with open(self.staging_path, "w+") as f:
                json.dump([], f)
        logger.debug(f"Opened local dataset at {self.path}")

    def pull(self, verbose=True):
        """
        Pulls the latest ``index.json``.

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
        Checks out a specific commit. This will delete any local changes in ``index.json``
        or ``associated_files``.

        :param verbose: If False, run git commands with the `-q` option.
        """
        checkout_cmd = ["git", "reset", "--hard"]
        if not verbose:
            checkout_cmd.append("-q")
        return subprocess.call(checkout_cmd + [commit_hash], cwd=self.path)

    def add_local_changes(self, skip_validation=False):
        """
        Stages changes to ``index.json`` and ``associated_files`` for the next commit.

        :param skip_validation: By default, ``index.json`` is validated against a schema.
            If the schema is incorrect and you're sure your ``index.json`` is valid, you can
            pass `True` to skip the check. In this case, please also submit a PR so we can
            update the schema.
        """
        if skip_validation:
            logger.warning(
                "Skipping index.json check. Please submit a PR if the schema should be changed."
            )
        elif not self.validate_index():
            logger.error("Not adding changes to index.json. Doesn't match schema.")
            logger.error(
                "You may be able to skip this check with '--skip-validation' if you're sure your file conforms."
            )
            exit(-1)
        return subprocess.call(
            ["git", "add", "index.json", "associated_files"], cwd=self.path
        )

    def commit(self, message, verbose=True):
        """
        Commit added changes to the local git repo, with the given commit `message`.

        :param verbose: If False, run git commands with the `-q` option.
        """
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
        # The subprocess will return a non-zero exit code even if it succeeded.
        # Check its output to determine whether it worked.
        push_proc = subprocess.run(
            ["git", "push"],
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        if "updated in conservator" not in push_proc.stdout:
            if "Everything up-to-date" in push_proc.stdout:
                logger.warning(push_proc.stdout)
            else:
                logger.error(
                    "Server did not accept changes to index.json:\n%s", push_proc.stdout
                )
                raise RuntimeError("Failed to push changes to index.json")
        self.pull(verbose)

    def push_staged_images(self, copy_to_data=True, tries=5):
        """
        Push the staged images.

        This reads the staged image paths, uploads them, adds metadata
        to ``index.json``, and deletes the staged image paths.

        :param copy_to_data: If `True`, copy the staged images to the cache and
            link with the data directory. This produces the same result as
            downloading the images back from conservator (but without downloading).
        :param tries: Specify a retry limit when recovering from HTTP 502 errors.
        """
        image_paths = self.get_staged_images()
        if len(image_paths) == 0:
            logger.info("No files to push.")
            return

        index = self.get_index()
        next_index = LocalDataset.get_max_frame_index(index) + 1
        for path in image_paths:
            image_info = LocalDataset.get_image_info(path)
            if image_info is None:
                logger.error(f"Skipping '{path}'")
                continue

            md5 = image_info["md5"]
            if not self.conservator.dvc_hash_exists(md5):
                self.upload_image(path, md5, tries=tries)
            else:
                logger.debug(f"File '{path}' already exists on conservator, skipping")

            # Dataset frames uploaded in this manner do not have a video.
            # They are considered "loose" frames and use the dataset's ID
            # as the video ID.
            video_id = index["datasetId"]
            frame_id = self.conservator.generate_id()

            del image_info["filename"]

            new_frame = {
                **image_info,
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
            index["frames"].append(new_frame)
            logger.debug(f"Added new DatasetFrame with id {frame_id}")

            if copy_to_data:
                os.makedirs(self.data_path, exist_ok=True)

                # First copy it to the cache:
                cache_path = self.get_cache_path(md5)
                cache_dir = os.path.split(cache_path)[0]
                os.makedirs(cache_dir, exist_ok=True)
                logger.debug(f"Copying file from '{path}' to '{cache_path}'")
                shutil.copyfile(path, cache_path)

                # Then link to data path:
                filename = f"video-{video_id}-frame-{next_index:06d}-{frame_id}.jpg"
                data_path = os.path.join(self.data_path, filename)
                logger.debug(f"Linking '{data_path}' to '{cache_path}'")
                os.link(cache_path, data_path)

            next_index += 1

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
        logger.info(f"Uploading '{path}'.")
        retry_count = 0
        while retry_count < tries:
            with open(path, "rb") as data:
                r = requests.put(url, data, headers=headers)
            if r.status_code == 502:
                retry_count += 1
                if retry_count < tries:
                    logger.info(f"Bad Gateway error, retrying {filename} ..")
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
                logger.error(f"Path '{image_path}' does not exist.")
                return
            if os.path.isdir(image_path):
                logger.error(f"Path '{image_path}' is a directory.")
                return
            if LocalDataset.get_image_info(image_path) is None:
                return

        # Then add absolute paths to staging file
        staged_images = self.get_staged_images()
        for image_path in image_paths:
            abspath = os.path.abspath(image_path)
            if abspath not in staged_images:
                logger.info(f"Adding '{abspath}' to staging file.")
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
            logger.error(f"'{path}' is not an image")
            return

        if image.format != "JPEG":
            logger.error(f"'{path}' is not a JPEG")
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
    def get_max_frame_index(index):
        """
        Returns the maximum frame index in a dataset's `index`.

        This only checks "loose" frames, that aren't a part of a specific video.
        """
        max_index = 0
        for f in index.get("frames", []):
            if f["datasetFrameId"] == f["videoMetadata"]["frameId"]:
                frame_index = f["videoMetadata"]["frameIndex"]
                max_index = max(max_index, frame_index)
        return max_index

    def get_cache_path(self, md5):
        return os.path.join(self.cache_path, md5[:2], md5[2:])

    def get_frames(self):
        with open(self.index_path) as f:
            data = json.load(f)
        return data.get("frames", [])

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
            logger.debug(f"Linking '{link_path}' to '{path}'")
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
            logger.warning(f"Cache file '{cache_path}' was empty, ignoring.")
            return False
        if not md5sum_file(cache_path) == md5:
            logger.warning(f"Cache file '{cache_path}' had invalid MD5, ignoring.")
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
        Downloads the files listed in ``index.json`` of the local dataset.

        :param include_analytics: If `True`, download analytic data to ``analyticsData/``.
        :param include_eight_bit: If `True`, download eight-bit images to ``data/``.
        :param process_count: Number of concurrent download processes. Passing `None`
            will use `os.cpu_count()`.
        :param use_symlink: If `True`, use symbolic links instead of hardlinks when linking the
            cache and data.
        :param no_meter: If 'True', don't display file download progress meters.
        :param tries: Specify a retry limit when recovering from connection errors.
        """
        if include_eight_bit:
            os.makedirs(self.data_path, exist_ok=True)

        if include_analytics:
            os.makedirs(self.analytics_path, exist_ok=True)

        logger.info(f"Getting frames from index.json...")
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

        # If frames were deleted from index.json, we need to clear them out of
        # the data directory. Because we have the cache, we can just delete everything.
        self.clean_data_dir()

        logger.info(f"Checking cache...")
        cache_hits = 0
        assets = []  # (path, name, url, paths_to_link, use_symlink)
        for md5, paths_to_link in hashes_required.items():
            cache_path = self.get_cache_path(md5)
            if self.exists_in_cache(md5):
                LocalDataset._add_links(cache_path, paths_to_link, use_symlink)
                cache_hits += 1
                logger.debug(f"Skipping {md5}: already downloaded.")
                continue
            url = self.conservator.get_dvc_hash_url(md5)
            asset = (cache_path, url, paths_to_link, use_symlink)
            logger.debug(f"Going to download {md5}")
            assets.append(asset)

        logger.info(f"Total frames: {frame_count}")
        logger.info(f"  Unique hashes: {len(hashes_required)}")
        logger.info(f"  Already downloaded: {cache_hits}")
        logger.info(f"  Missing: {len(assets)}")
        logger.info(
            f"Going to download {len(assets)} new frames using {process_count} processes."
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
                            f"Download to {entry[0]} seems to have failed. Retrying .."
                        )
                    else:
                        logger.error(
                            f"Download to {entry[0]} seems to have failed. Try again, or submit an issue."
                        )
                    failures += 1
                    retry_assets.append(entry)
            if failures >= len(assets):
                logger.error("All downloads failed!")
                break
            elif failures:
                current_assets = retry_assets
                progress_msg = "Retrying missing frames"
            else:
                break

        successes = len(assets) - failures

        logger.info(f"Downloads attempted: {len(assets)}")
        logger.info(f"  Reported {sum(results)} successes.")
        logger.info(f"  Successful downloads: {successes}")
        logger.info(f"  Failed downloads: {failures}")

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
                f"Dataset {dataset.name} not available for cloning, retry in {timeout} seconds..."
            )
            time.sleep(timeout)
            dataset.populate(["name", "repository.master"])

        if not dataset.has_field("repository.master"):
            logging.error(f"Dataset {dataset.name} has no repository. Unable to clone.")
            logging.error(
                "This dataset can be fixed by browsing to it in Conservator Web UI and clicking 'Commit Changes'."
            )
            return

        if clone_path is None:
            clone_path = dataset.name

        if os.path.exists(clone_path):
            logging.error(f"Path {clone_path} already exists, can't clone.")
            return

        url = dataset.get_git_url()
        clone_cmd = ["git", "clone"]
        if not verbose:
            clone_cmd.append("-q")
        clone_cmd += [url, clone_path]
        r = subprocess.call(clone_cmd)
        if r != 0:
            logging.error(f"Error {r} when cloning.")
            return

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

        return LocalDataset(dataset._conservator, clone_path)

    def validate_index(self):
        """Validates that ``index.json`` matches the expected
        JSON Schema."""
        schema_json = self.conservator.query(Query.validation_schema)
        schema = json.loads(schema_json)

        try:
            with open(self.index_path) as index:
                index_data = json.load(index)
            jsonschema.validate(index_data, schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(e.message)
            logger.debug(e)
        return False
