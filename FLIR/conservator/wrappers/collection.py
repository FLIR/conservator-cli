import functools
import os

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Query,
    Mutation,
    CreateCollectionInput,
    DeleteCollectionInput,
)
from FLIR.conservator.local_dataset import LocalDataset
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.util import download_files
from FLIR.conservator.wrappers.type_proxy import requires_fields
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.wrappers.video import Video
from FLIR.conservator.wrappers.image import Image
from FLIR.conservator.wrappers.dataset import Dataset


class InvalidRemotePathException(Exception):
    pass


class Collection(QueryableType):
    underlying_type = schema.Collection
    by_id_query = schema.Query.collection
    search_query = schema.Query.collections

    def create_video(self, filename, fields=None):
        """
        Create a new :class:`~FLIR.conservator.wrappers.video.Video` within
        this collection, returning it with the specified `fields`.
        """
        return Video.create(self._conservator, filename, self.id, fields)

    def create_child(self, name, fields=None):
        """
        Create a new child collection with the given `name`, returning it
        with the specified `fields`.
        """
        _input = CreateCollectionInput(name=name, parent_id=self.id)
        result = self._conservator.query(
            Mutation.create_collection,
            operation_base=Mutation,
            input=_input,
            fields=fields,
        )
        return Collection(self._conservator, result)

    @requires_fields("path")
    def get_child(self, name, make_if_no_exists=False, fields=None):
        """
        Returns the child collection with the given `name` and specified `fields`.

        If it does not exist, and `make_if_no_exists` is `True`, it will be created.
        """
        path = os.path.join(self.path, name)
        try:
            child = Collection.from_remote_path(
                conservator=self._conservator,
                path=path,
                make_if_no_exist=False,
                fields=fields,
            )
        except InvalidRemotePathException:
            if make_if_no_exists:
                return self.create_child(name, fields)
            raise
        return child

    def generate_signed_locker_upload_url(self, filename, content_type):
        """
        Returns a signed url for uploading a new file locker file with the given `filename` and
        `content_type`.
        """
        result = self._conservator.query(
            Mutation.generate_signed_collection_file_locker_upload_url,
            operation_base=Mutation,
            dataset_id=self.id,
            content_type=content_type,
            filename=filename,
        )
        return result.signed_url

    @classmethod
    def create_root(cls, conservator, name, fields=None):
        """
        Create a new root collection with the specified `name` and
        return it with the specified `fields`.

        This requires your account to have privilege to create new projects.
        """
        project = conservator.projects.create(name, fields="root_collection.id")
        root_collection = project.root_collection
        root_collection.populate(fields)
        return root_collection

    @classmethod
    def create_from_remote_path(cls, conservator, path, fields=None):
        """
        Return a new collection at the specified `path`, with the given `fields`,
        creating new collections as necessary.
        """
        if not path.startswith("/"):
            path = "/" + path

        split_path = path.split("/")[1:]
        root_path = "/" + split_path[0]
        temp_fields = ["id", "path"]
        try:
            root = Collection.from_remote_path(
                conservator, path=root_path, make_if_no_exist=False, fields=temp_fields
            )
        except InvalidRemotePathException:
            root = Collection.create_root(
                conservator, name=root_path, fields=temp_fields
            )

        current = root
        for name in split_path[1:]:
            current = current.get_child(
                name, make_if_no_exists=True, fields=temp_fields
            )

        current.populate(fields)
        return current

    @classmethod
    def from_remote_path(cls, conservator, path, make_if_no_exist=False, fields=None):
        """
        Returns a collection at the specified `path`, with the specified `fields`.
        If `make_if_no_exist` is `True`, then collection(s) will be created to
        reach that path if it doesn't exist.
        """
        collection = conservator.query(
            Query.collection_by_path, path=path, fields=fields
        )
        if collection is None:
            if make_if_no_exist:
                return cls.create_from_remote_path(conservator, path, fields)
            else:
                raise InvalidRemotePathException(path)
        return Collection(conservator, collection)

    def recursively_get_children(self, include_self=False, fields=None):
        """
        Yields all child collections recursively.

        :param include_self: If `True`, yield this collection too.
        :param fields: The `fields` to populate on children.
        """
        fields = FieldsRequest.create(fields)
        fields.include("children.id")
        self.populate(fields)

        if include_self:
            yield self

        collections = [*self.children]

        while len(collections) > 0:
            collection = collections.pop()
            collection.populate(fields)
            yield collection
            collections.extend(collection.children)

    def get_images(self, fields=None):
        """Returns a query for all images in this collection."""
        images = PaginatedQuery(
            self._conservator, Image, Query.images, fields=fields, collection_id=self.id
        )
        return images

    def recursively_get_images(self, fields=None):
        """Yields all images in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_images(fields)

    def get_videos(self, fields=None):
        """Returns a query for all videos in this collection."""
        videos = PaginatedQuery(
            self._conservator, Video, Query.videos, fields=fields, collection_id=self.id
        )
        return videos

    def recursively_get_videos(self, fields=None):
        """Yields all videos in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_videos(fields)

    def get_media(self, fields=None):
        """
        Yields all videos, then images in this collection.

        :param fields: The `fields` to include in the media. All
            fields must exist on both Image and Video types.
        """
        yield from self.get_videos(fields=fields)
        yield from self.get_images(fields=fields)

    def recursively_get_media(self, fields=None):
        """Yields all videos and images in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_media(fields)

    def get_datasets(self, fields=None):
        """Returns a query for all datasets in this collection."""
        datasets = PaginatedQuery(
            self._conservator,
            Dataset,
            Query.datasets,
            fields=fields,
            collection_id=self.id,
        )
        return datasets

    def delete(self):
        """
        Delete the collection.
        """
        input_ = DeleteCollectionInput(id=self.id)
        self._conservator.query(
            Mutation.delete_collection, operation_base=Mutation, input=input_
        )

    @requires_fields("name", "file_locker_files", "child_ids")
    def download(
        self,
        path,
        include_datasets=False,
        include_metadata=False,
        include_associated_files=False,
        include_media=False,
        recursive=False,
    ):
        """Downloads this collection to the `path` specified,
        with the specified assets included."""
        path = os.path.join(path, self.name)
        os.makedirs(path, exist_ok=True)

        if include_metadata:
            self.download_metadata(path)
        if include_associated_files:
            self.download_associated_files(path)
        if include_media:
            self.download_media(path)
        if include_datasets:
            self.download_datasets(path)
        if recursive:
            for id_ in self.child_ids:
                child = Collection.from_id(self._conservator, id_)
                child.download(
                    path,
                    include_datasets,
                    include_metadata,
                    include_associated_files,
                    include_media,
                    recursive,
                )

    def download_metadata(self, path):
        """Downloads image and video metadata to ``media_metadata/``."""
        path = os.path.join(path, "media_metadata")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest.create(["metadata", "filename"])

        videos = self.get_videos(fields=fields)
        for video in videos:
            video.download_metadata(path)
        images = self.get_images(fields=fields)
        for image in images:
            image.download_metadata(path)

    @requires_fields("file_locker_files")
    def download_associated_files(self, path, no_meter=False):
        """Downloads associated files (from file locker) to
        ``associated_files/``."""
        path = os.path.join(path, "associated_files")
        os.makedirs(path, exist_ok=True)
        assets = [(path, file.name, file.url) for file in self.file_locker_files]
        download_files(assets, no_meter=no_meter)

    def download_media(self, path, no_meter=False):
        """Downloads videos and images."""
        self.download_videos(path, no_meter=no_meter)
        self.download_images(path, no_meter=no_meter)

    def download_videos(self, path, no_meter=False):
        """Downloads videos to ``videos/``."""
        path = os.path.join(path, "videos")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "url")
        videos = self.get_videos(fields=fields)
        assets = [(path, video.filename, video.url) for video in videos]
        download_files(assets, no_meter=no_meter)

    def download_images(self, path, no_meter=False):
        """Downloads images to ``images/``."""
        path = os.path.join(path, "images")
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "url")
        images = self.get_images(fields=fields)
        assets = [(path, image.filename, image.url) for image in images]
        download_files(assets, no_meter=no_meter)

    def download_datasets(self, path, no_meter=False):
        """Clones and pulls all datasets in the collection."""
        fields = FieldsRequest()
        fields.include_field("name", "repository.master")
        datasets = self.get_datasets(fields=fields)
        for dataset in datasets:
            clone_path = os.path.join(path, dataset.name)
            lds = LocalDataset.clone(dataset, clone_path=clone_path)
            lds.download(no_meter=no_meter)
