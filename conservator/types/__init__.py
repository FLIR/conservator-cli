import json
import multiprocessing
import os
import subprocess

from conservator.generated.schema import Query
from conservator.types.downloadable import DownloadableType, RecursiveDownload, AssociatedFilesDownload, \
    FieldAsJsonDownload, SubtypeDownload, DatasetsFromCollectionDownload
from conservator.generated import schema
from conservator.types.searchable import SearchableType
from conservator.types.type_proxy import TypeProxy

__all__ = [
    "Project",
    "Video",
    "Dataset",
    "Collection",
    "SearchableType",
    "DownloadableType",
    "TypeProxy",
]

from conservator.util import FileDownloadException, download_file


class Project(SearchableType, DownloadableType):
    underlying_type = schema.Project
    search_query = schema.Query.projects
    by_id_query = schema.Query.project
    problematic_fields = []
    downloadable_assets = {}


class Dataset(SearchableType, DownloadableType):
    underlying_type = schema.Dataset
    search_query = schema.Query.datasets
    by_id_query = schema.Query.dataset
    problematic_fields = ["shared_with"]
    downloadable_assets = {}

    def get_git_url(self):
        return f"https://{self._conservator.get_git_user()}@{self._conservator.get_domain()}/git/dataset_{self.id}"

    def get_dvc_url(self):
        return f"https://{self._conservator.get_git_user()}@{self._conservator.get_domain()}/dvc"

    def clone(self, path):
        subprocess.call(["git", "clone",
                         self.get_git_url(),
                         path])

    def pull(self, path, include_analytics=False, include_eight_bit=True, process_count=None):
        data_dir = os.path.join(path, 'data')
        if include_eight_bit:
            os.makedirs(data_dir, exist_ok=True)

        analytics_dir = os.path.join(path, 'analyticsData')
        if include_analytics:
            os.makedirs(analytics_dir, exist_ok=True)

        pool = multiprocessing.Pool(process_count)  # defaults to CPU count

        index_file = os.path.join(path, "index.json")
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

    def download(self, path, pull=True):
        self.populate("name")
        path = os.path.join(path, self.name)
        os.makedirs(path, exist_ok=True)
        self.clone(path)
        if pull:
            self.pull(path)


class Video(SearchableType, DownloadableType):
    underlying_type = schema.Video
    search_query = schema.Query.videos
    by_id_query = schema.Query.video
    problematic_fields = ["shared_with"]
    downloadable_assets = {}

    def download(self, path):
        pass


class Collection(SearchableType, DownloadableType):
    underlying_type = schema.Collection
    search_query = schema.Query.collections
    by_id_query = schema.Query.collection
    problematic_fields = []
    downloadable_assets = {
        "videos": SubtypeDownload(Video, "video_ids"),
        "associated_files": AssociatedFilesDownload(),
        # "images": SubtypeDownload(None, "image_ids"),
        "datasets": DatasetsFromCollectionDownload(),
        "recursive": RecursiveDownload("child_ids"),
    }

    def get_datasets(self):
        dataset_objs = self._conservator.query(Query.get_first_ndatasets,
                                               id=self.id,
                                               search_text="",
                                               n=200,
                                               include_fields=["id", "name"])
        datasets = []
        for dataset_obj in dataset_objs:
            datasets.append(Dataset(self._conservator, dataset_obj))
        return datasets

    def download(self, path):
        raise NotImplementedError("Collections are containers.  Use download_assets instead.")

    def download_assets(self, path,
                        include_datasets=False,
                        include_media=False,
                        include_associated_files=False,
                        include_videos=False,
                        include_images=False,
                        recursive=False,
                        **kwargs):
        """
        Download a Collection to the specified ``path``.

        :param path: The directory to download this collection into. Files will be saved
            at ``os.path.join(path, Collection.name)``.
        :param recursive: If ``True``, recursively download this collection's children
            as subdirectories.
        :param include_datasets: If ``True``, download all related datasets.
        :param include_media: If ``True``, equivalent to passing ``include_videos=True`` and ``include_images=True``.
        :param include_videos: If ``True``, download videos.
        :param include_images: If ``True``, download images.
        :param include_associated_files: If ``True``, download file locker files, such as the word cloud.
        """
        assets = []
        if include_datasets:
            assets.append("datasets")
        if include_media or include_videos:
            assets.append("videos")
        if include_media or include_images:
            assets.append("images")
        if include_associated_files:
            assets.append("associated_files")
        if recursive:
            assets.append("recursive")

        super().download_assets(path, assets, **kwargs)
