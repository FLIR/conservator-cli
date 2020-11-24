"""
This modules contains types that wrap generated SGQLC types.

These wrapped types all extend :class:`TypeProxy`, and contain
a private instance of the underling SGQLC object. Initialized fields
can be accessed on the :class:`TypeProxy` instance. :class:`TypeProxy`
also provides functions to fetch new fields from Conservator.

Many of these types will also implement various Abstract
Class Types, to add functionality such as Downloading, Uploading,
Loading from Directory, etc.

Often they will include additional functions that wrap SGQLC queries.
For instance, a :class:`Collection` has :func:`Collection.get_datasets`,
which runs the GraphQL query for a collection's datasets--and returns
them as proxied :class:`Dataset` objects.
"""
import json
import multiprocessing
import os
import subprocess

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated import schema
from FLIR.conservator.types.type_proxy import TypeProxy
from FLIR.conservator.util import download_file, FileDownloadException


class Collection(TypeProxy):
    underlying_type = schema.Collection
    by_id_query = schema.Query.collection
    search_query = schema.Query.collections


class MissingFieldException(Exception):
    pass


class Dataset(TypeProxy):
    underlying_type = schema.Dataset
    by_id_query = schema.Query.dataset
    search_query = schema.Query.datasets

    def get_git_url(self):
        """Returns the Git URL used for cloning this Dataset."""
        return f"{self._conservator.get_authenticated_url()}/git/dataset_{self.id}"

    def get_dvc_url(self):
        """Returns the DVC URL used for downloading files."""
        return f"{self._conservator.get_authenticated_url()}/dvc"

    def clone(self, path="."):
        """Clone this Dataset into a subdirectory of `path` based on
        the Dataset's name.

        For instance, if you pass `path`=``~/Desktop``, and want to download a Dataset
        called ``MyFirstDataset``, it will be cloned into ``~/Desktop/My First_Dataset``.
        """
        fields = FieldsRequest(include_fields=("name", "repository.master"))
        self.populate(fields)
        if not self.has_field("repository.master"):
            raise MissingFieldException(f"Dataset '{self.name}' does not have an associated git repository")

        path = os.path.join(path, self.name)
        if os.path.exists(path):
            raise FileExistsError(f"Cannot clone to '{path}', already exists.")

        url = self.get_git_url()
        subprocess.call(["git", "clone", url, path])

    @classmethod
    def from_path(cls, conservator, path="."):
        """Returns a new Dataset instance using the ID found in ``index.json``
        at the provided `path`
        """
        index_file = os.path.join(path, "index.json")
        if not os.path.exists(index_file):
            raise FileNotFoundError("Missing index.json, check the path")

        with open(index_file) as f:
            data = json.load(f)
            return cls.from_id(conservator, data['datasetId'])

    def pull(self, path=".", include_analytics=False, include_eight_bit=True, process_count=None):
        """
        Downloads the files listed in ``index.json`` at the provided `path`.

        :param include_analytics: If `True`, download analytic data to ``analyticsData/``.
        :param include_eight_bit: If `True`, download eight-bit images to ``data/``.
        """
        index_file = os.path.join(path, "index.json")
        if not os.path.exists(index_file):
            raise FileNotFoundError("Missing index.json, check the path")

        data_dir = os.path.join(path, 'data')
        if include_eight_bit:
            os.makedirs(data_dir, exist_ok=True)

        analytics_dir = os.path.join(path, 'analyticsData')
        if include_analytics:
            os.makedirs(analytics_dir, exist_ok=True)

        pool = multiprocessing.Pool(process_count)  # defaults to CPU count

        assets = []  # (md5, path, name, url)
        base_url = self.get_dvc_url()
        with open(index_file) as f:
            data = json.load(f)
            for frame in data.get('frames', []):
                video_metadata = frame.get('videoMetadata', {})
                video_id = video_metadata.get("videoId", "")
                frame_index = video_metadata['frameIndex']
                dataset_frame_id = frame['datasetFrameId']
                if include_eight_bit:
                    md5 = frame['md5']
                    url = f"{base_url}/{md5[:2]}/{md5[2:]}"
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.jpg"
                    assets.append((md5, data_dir, name, url))

                if include_analytics and ('analyticsMd5' in frame):
                    md5 = frame['analyticsMd5']
                    url = f"{base_url}/{md5[:2]}/{md5[2:]}"
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.tiff"
                    assets.append((md5, analytics_dir, name, url))

        results = pool.starmap(self.download_image, assets)

        # See if we have any errors
        total = len(results)
        num_errors = results.count('ERROR')
        print(f"Number of Files: {total - num_errors}, Errors: {num_errors}")

    @staticmethod
    def download_image(md5, path, name, url):
        # TODO: Use a cache and os.link
        try:
            download_file(path, name, url)
        except FileDownloadException:
            print(f"Error downloading {url}")
            return "ERROR"

        # Hard link named image file
        # TODO os.link(filename, os.path.join(folder, imageFilename))
        return True


class Project(TypeProxy):
    underlying_type = schema.Project
    by_id_query = schema.Query.project
    search_query = schema.Query.projects


class Video(TypeProxy):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos
