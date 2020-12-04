import functools
import os

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.util import download_files
from FLIR.conservator.types.type_proxy import TypeProxy, requires_fields
from FLIR.conservator.types.video import Video
from FLIR.conservator.types.image import Image
from FLIR.conservator.types.dataset import Dataset


class Collection(TypeProxy):
    underlying_type = schema.Collection
    by_id_query = schema.Query.collection
    search_query = schema.Query.collections

    @classmethod
    def from_remote_path(cls, conservator, path, fields=None):
        collection = conservator.query(Query.collection_by_path, path=path, fields=fields)
        if collection is not None:
            return Collection(conservator, collection)

    def get_images(self, fields=None):
        """Returns a query for all images in this collection."""
        images = PaginatedQuery(self._conservator, Image, Query.datasets,
                                fields=fields, collection_id=self.id)
        return images

    def get_videos(self, fields=None):
        """Returns a query for all videos in this collection."""
        videos = PaginatedQuery(self._conservator, Video, Query.videos,
                                fields=fields, collection_id=self.id)
        return videos

    def get_datasets(self, fields=None):
        """Returns a query for all datasets in this collection."""
        datasets = PaginatedQuery(self._conservator, Dataset, Query.datasets,
                                  fields=fields, collection_id=self.id)
        return datasets

    @requires_fields("name", "file_locker_files", "child_ids")
    def download(self, path,
                 include_datasets=False,
                 include_video_metadata=False,
                 include_associated_files=False,
                 include_media=False,
                 recursive=False):
        """Downloads this collection to the `path` specified,
        with the specified assets included."""
        path = os.path.join(path, self.name)
        os.makedirs(path, exist_ok=True)

        if include_video_metadata:
            self.download_video_metadata(path)
        if include_associated_files:
            self.download_associated_files(path)
        if include_media:
            self.download_media(path)
        if include_datasets:
            self.download_datasets(path)
        if recursive:
            for id_ in self.child_ids:
                child = Collection.from_id(self._conservator, id_)
                child.download(path,
                               include_datasets,
                               include_video_metadata,
                               include_associated_files,
                               include_media,
                               recursive)

    def download_video_metadata(self, path):
        """Downloads video metadata to ``video_metadata/``."""
        path = os.path.join(path, "video_metadata")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("metadata", "filename")
        videos = self.get_videos(fields=fields)
        for video in videos:
            video.download_metadata(path)

    @requires_fields("file_locker_files")
    def download_associated_files(self, path):
        """Downloads associated files (from file locker) to
        ``associated_files/``."""
        path = os.path.join(path, "associated_files")
        os.makedirs(path, exist_ok=True)
        assets = [(path, file.name, file.url) for file in self.file_locker_files]
        download_files(assets)

    def download_media(self, path):
        """Downloads videos and images."""
        self.download_videos(path)
        self.download_images(path)

    def download_videos(self, path):
        """Downloads videos to ``videos/``."""
        path = os.path.join(path, "videos")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "url")
        videos = self.get_videos(fields=fields)
        assets = [(path, video.filename, video.url) for video in videos]
        download_files(assets)

    def download_images(self, path):
        """Downloads images to ``images/``."""
        path = os.path.join(path, "images")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "url")
        images = self.get_images(fields=fields)
        assets = [(path, image.filename, image.url) for image in images]
        download_files(assets)

    def download_datasets(self, path):
        """Clones and pulls all datasets in the collection."""
        fields = FieldsRequest()
        fields.include_field("name", "repository.master")
        datasets = self.get_datasets(fields=fields)
        for dataset in datasets:
            dataset.clone(path)
            dataset.pull(os.path.join(path, dataset.name))
