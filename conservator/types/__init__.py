import os

from conservator.types.downloadable import DownloadableType
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


class Video(SearchableType, DownloadableType):
    underlying_type = schema.Video
    search_query = schema.Query.videos
    by_id_query = schema.Query.video
    problematic_fields = ["shared_with"]
    downloadable_assets = {}


class Collection(SearchableType, DownloadableType):
    underlying_type = schema.Collection
    search_query = schema.Query.collections
    by_id_query = schema.Query.collection
    problematic_fields = []
    downloadable_assets = {
        "videos": None,
        "associated_files": None,
        "images": None,
        "metadata": None,
        "recursive": None,
    }

    def download_assets(self, path,
                        include_media=False,
                        include_associated_files=False,
                        include_videos=False,
                        include_images=False,
                        include_metadata=False,
                        recursive=False):
        """
        Download a Collection to the specified ``path``.

        :param path: The directory to download this collection into. Files will be saved
            at ``os.path.join(path, Collection.name)``.
        :param recursive: If ``True``, recursively download this collection's children
            as subdirectories.
        :param include_media: If ``True``, equivalent to passing ``include_videos=True`` and ``include_images=True``.
        :param include_videos: If ``True``, download videos.
        :param include_images: If ``True``, download images.
        :param include_associated_files: If ``True``, download file locker files, such as the word cloud.
        :param include_metadata: "If ``True``, download a JSON file containing metadata for each video
        """
        assets = []
        if include_media or include_videos:
            assets.append("videos")
        if include_media or include_images:
            assets.append("images")
        if include_associated_files:
            assets.append("associated_files")
        if include_metadata:
            assets.append("metadata")
        if recursive:
            assets.append("recursive")

        super().download_assets(path, assets)
