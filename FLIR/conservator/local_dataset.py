#!/usr/bin/env python
import subprocess
import os
import json
import hashlib
import shutil
import requests
import logging

from PIL import Image
from FLIR.conservator.util import download_files


logger = logging.getLogger(__name__)


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
        self.staging_path = os.path.join(self.path, ".staging.json")
        self.data_path = os.path.join(self.path, "data")
        self.analytics_path = os.path.join(self.path, "analyticsData")
        if not os.path.exists(self.index_path):
            return
        if not os.path.exists(self.staging_path):
            with open(self.staging_path, "w+") as f:
                json.dump([], f)
        logger.debug(f"Opened local dataset at {self.path}")

    def pull(self):
        """
        Pulls the latest ``index.json``.
        """
        subprocess.call(["git", "fetch"], cwd=self.path)
        return subprocess.call(
            ["git", "checkout", "origin/master", "-B", "master"], cwd=self.path
        )

    def checkout(self, commit_hash):
        """
        Checks out a specific commit. This will delete any local changes.
        """
        return subprocess.call(["git", "reset", "--hard", commit_hash], cwd=self.path)

    def add_index(self):
        """
        Stages changes to ``index.json`` for the next commit.
        """
        return subprocess.call(["git", "add", "index.json"], cwd=self.path)

    def commit(self, message):
        """
        Commit added changes to the local git repo, with the given commit `message`.
        """
        return subprocess.call(["git", "commit", "-m", message], cwd=self.path)

    def push_commits(self):
        """
        Push the git repo.
        """
        subprocess.call(
            ["git", "push"],
            cwd=self.path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # changes wont appear to be pushed, but they were. so we pull
        self.pull()

    def push_staged_images(self):
        """
        Push the staged images.

        This reads the staged image paths, uploads them, adds metadata
        to ``index.json``, and deletes the staged image paths.
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
                self.upload_image(path, md5)

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

            if os.path.exists(self.data_path):
                # Since data path exists, chances are media files are downloaded.
                # We should copy this image to the data path so it doesn't have to
                # be repulled.
                filename = f"video-{video_id}-frame-{next_index:06d}-{frame_id}.jpg"
                data_path = os.path.join(self.data_path, filename)
                logger.debug(f"Copying file from '{path}' to '{data_path}'")
                shutil.copyfile(path, data_path)

            next_index += 1

        with open(self.index_path, "w") as f:
            json.dump(index, f, indent=4, sort_keys=True, separators=(",", ": "))
        with open(self.staging_path, "w") as f:
            json.dump([], f)

    def upload_image(self, path, md5):
        url = self.conservator.get_dvc_hash_url(md5)
        filename = os.path.split(path)[1]
        print(filename)
        headers = {
            "Content-type": "image/jpeg",
            "x-amz-meta-originalfilename": filename,
        }
        print(headers)
        logger.info(f"Uploading '{path}'.")
        with open(path, "rb") as data:
            r = requests.put(url, data, headers=headers)
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
                logger.debug(f"Adding '{abspath}' to staging file.")
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
            "md5": hashlib.md5(open(path, "rb").read()).hexdigest(),
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

    def download(
        self, include_analytics=False, include_eight_bit=True, process_count=None
    ):
        """
        Downloads the files listed in ``index.json`` of the local dataset.

        :param include_analytics: If `True`, download analytic data to ``analyticsData/``.
        :param include_eight_bit: If `True`, download eight-bit images to ``data/``.
        :param process_count: Number of concurrent download processes. Defaults to the number of
            processors on the machine.
        """
        if include_eight_bit:
            os.makedirs(self.data_path, exist_ok=True)

        if include_analytics:
            os.makedirs(self.analytics_path, exist_ok=True)

        assets = []  # (path, name, url)
        with open(self.index_path) as f:
            data = json.load(f)
            for frame in data.get("frames", []):
                video_metadata = frame.get("videoMetadata", {})
                video_id = video_metadata.get("videoId", "")
                frame_index = video_metadata["frameIndex"]
                dataset_frame_id = frame["datasetFrameId"]
                if include_eight_bit:
                    md5 = frame["md5"]
                    url = self.conservator.get_dvc_hash_url(md5)
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.jpg"
                    assets.append((self.data_path, name, url))

                if include_analytics and ("analyticsMd5" in frame):
                    md5 = frame["analyticsMd5"]
                    url = self.conservator.get_dvc_hash_url(md5)
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.tiff"
                    assets.append((self.analytics_path, name, url))

        results = download_files(assets, process_count)

        # See if we have any errors
        total = len(results)
        success = sum(results)
        print(f"Number of Files: {success}, Errors: {total - success}")

    @staticmethod
    def clone(dataset, clone_path=None):
        """Clone a `dataset` to a local path, returning a :class:`LocalDatasetOperations`.

        :param dataset: The dataset to clone. It must have a repository registered
            in Conservator.
        :param clone_path: The path where the git repo should be created. If `None`,
            the dataset is cloned into a subdirectory of the current path, using
            the Dataset's name.
        """
        dataset.populate(["name", "repository.master"])
        if not dataset.has_field("repository.master"):
            logging.error("Dataset has no repository. Unable to clone.")
            return

        if clone_path is None:
            clone_path = f"./{dataset.name}"

        url = dataset.get_git_url()
        r = subprocess.call(["git", "clone", url, clone_path])
        if r != 0:
            logging.error(f"Error {r} when cloning.")
            return

        # TODO: remove email from config, use User query with cache
        email = dataset._conservator.config.email
        subprocess.call(["git", "config", "user.email", email.lower()], cwd=clone_path)

        return LocalDataset(dataset._conservator, clone_path)
