import logging
import os
import re

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.file_transfers import DownloadRequest
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Query,
    Mutation,
    CreateCollectionInput,
    DeleteCollectionInput,
    MoveAssetInput,
)
from FLIR.conservator.local_dataset import LocalDataset
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.wrappers.type_proxy import requires_fields
from FLIR.conservator.wrappers.file_locker import FileLockerType
from FLIR.conservator.wrappers.queryable import QueryableType


logger = logging.getLogger(__name__)


class InvalidRemotePathException(Exception):
    pass


class RemotePathExistsException(Exception):
    pass


class Collection(QueryableType, FileLockerType):
    underlying_type = schema.Collection
    by_id_query = schema.Query.collection
    search_query = schema.Query.collections

    # name of id field in mutations when not simply 'id'
    id_type = "collection_id"

    # file-locker operations
    file_locker_gen_url = Mutation.generate_signed_collection_file_locker_upload_url
    file_locker_remove = Mutation.remove_collection_file_locker_file

    def create_child(self, name, fields=None):
        """
        Create a new child collection with the given `name`, returning it
        with the specified `fields`.
        """
        _input = CreateCollectionInput(name=name, parent_id=self.id)
        return self._conservator.query(
            Mutation.create_collection,
            input=_input,
            fields=fields,
        )

    @requires_fields("path")
    def get_child(self, name, make_if_no_exists=False, fields=None):
        """
        Returns the child collection with the given `name` and specified `fields`.

        If it does not exist, and `make_if_no_exists` is `True`, it will be created.
        """
        path = "/".join([self.path, name])
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

        If the path already exists, raises :class:`RemotePathExistsException`.
        """
        if not path.startswith("/"):
            path = "/" + path

        try:
            collection = Collection.from_remote_path(
                conservator, path=path, make_if_no_exist=False, fields="id"
            )
            if collection is not None:
                raise RemotePathExistsException(f"Path '{path}' already exists.")
        except InvalidRemotePathException:
            pass

        split_path = path.split("/")[1:]
        root_path = "/" + split_path[0]
        temp_fields = ["id", "path"]

        try:
            root = Collection.from_remote_path(
                conservator, path=root_path, make_if_no_exist=False, fields=temp_fields
            )
        except InvalidRemotePathException:
            root = Collection.create_root(
                conservator, name=split_path[0], fields=temp_fields
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
        # Remove repeated '/' characters.
        clean_path = re.sub("/+", "/", path)

        if not path.startswith("/"):
            clean_path = "/" + path

        if clean_path.endswith("/"):
            clean_path = clean_path[:-1]

        collection = conservator.query(
            Query.collection_by_path, path=clean_path, fields=fields
        )
        if collection is None:
            if make_if_no_exist:
                return cls.create_from_remote_path(conservator, clean_path, fields)
            else:
                raise InvalidRemotePathException(clean_path)
        return collection

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

    def get_images(self, fields=None, search_text=""):
        """Returns a query for all images in this collection."""
        images = PaginatedQuery(
            self._conservator,
            query=Query.images,
            fields=fields,
            search_text=search_text,
            collection_id=self.id,
        )
        return images

    def recursively_get_images(self, fields=None, search_text=""):
        """Yields all images in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_images(fields, search_text)

    def get_videos(self, fields=None, search_text=""):
        """Returns a query for all videos in this collection."""
        videos = PaginatedQuery(
            self._conservator,
            query=Query.videos,
            fields=fields,
            search_text=search_text,
            collection_id=self.id,
        )
        return videos

    def recursively_get_videos(self, fields=None, search_text=""):
        """Yields all videos in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_videos(fields, search_text)

    def get_media(self, fields=None, search_text=""):
        """
        Yields all videos, then images in this collection.

        :param fields: The `fields` to include in the media. All
            fields must exist on both Image and Video types.
        """
        yield from self.get_videos(fields=fields, search_text=search_text)
        yield from self.get_images(fields=fields, search_text=search_text)

    def recursively_get_media(self, fields=None, search_text=""):
        """Yields all videos and images in this and child collections recursively"""
        for collection in self.recursively_get_children(include_self=True, fields="id"):
            yield from collection.get_media(fields, search_text)

    def get_datasets(self, fields=None, search_text=""):
        """Returns a query for all datasets in this collection."""
        datasets = PaginatedQuery(
            self._conservator,
            query=Query.datasets,
            fields=fields,
            search_text=search_text,
            collection_id=self.id,
        )
        return datasets

    def create_dataset(self, name, fields=None):
        return self._conservator.datasets.create(
            name, collections=[self], fields=fields
        )

    def remove_media(self, media_id):
        """
        Remove given media from this collection.
        """
        input_ = MoveAssetInput(asset_id=media_id, from_collection=self.id)
        return self._conservator.query(
            Mutation.move_video,
            input=input_,
        )

    def move(self, parent):
        """
        Move the collection into another collection.
        """
        result = self._conservator.query(
            Mutation.move_collection,
            id=self.id,
            parent_id=parent.id,
        )
        self.populate(fields="path")
        return result

    def delete(self):
        """
        Delete the collection.
        """
        input_ = DeleteCollectionInput(id=self.id)
        return self._conservator.query(
            Mutation.delete_collection,
            input=input_,
        )

    @requires_fields("name", "file_locker_files", "child_ids")
    def download(
        self,
        path=None,
        include_datasets=False,
        include_metadata=False,
        include_associated_files=False,
        include_media=False,
        preview_videos=False,
        recursive=False,
    ):
        """
        Downloads this collection to the `path` specified, with the specified assets
        included. If `path` is `None` or not given, downloaded to a directory with
        the name of the collection.
        """
        if path is None:
            path = self.name

        os.makedirs(path, exist_ok=True)

        if include_metadata:
            self.download_metadata(path)
        if include_associated_files:
            self.download_associated_files(path)
        if include_media:
            self.download_media(path, preview_videos=preview_videos)
        if include_datasets:
            self.download_datasets(path)
        if recursive:
            for id_ in self.child_ids:
                child = Collection.from_id(self._conservator, id_)
                child.populate("name")
                child_path = os.path.join(path, child.name)
                child.download(
                    child_path,
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

    def download_media(self, path, preview_videos=False, no_meter=False):
        """
        Downloads videos and images.  If `preview_videos` is set, download
        preview videos in place of full videos.
        """
        self.download_videos(path, preview_videos=preview_videos, no_meter=no_meter)
        self.download_images(path, no_meter=no_meter)

    def download_videos(self, path, preview_videos=False, no_meter=False):
        """
        Downloads videos to given path.  If `preview_videos` is set, download
        preview videos in place of full videos.
        """
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "preview_video_url", "url", "md5")
        downloads = []
        for video in self.get_videos(fields=fields):
            video_url = video.url
            if preview_videos:
                if video.preview_video_url:
                    video_url = video.preview_video_url
                else:
                    logger.warning(
                        "No preview available for '%s`, downloading full video",
                        video.filename,
                    )
            local_path = os.path.join(path, video.filename)
            download = DownloadRequest(
                url=video_url, local_path=local_path, expected_md5=video.md5
            )
            downloads.append(download)
        self._conservator.files.download_many(downloads, no_meter=no_meter)

    def download_images(self, path, no_meter=False):
        """Downloads images to given path."""
        os.makedirs(path, exist_ok=True)
        fields = FieldsRequest()
        fields.include_field("filename", "url", "md5")
        downloads = []
        for image in self.get_images(fields=fields):
            local_path = os.path.join(path, image.filename)
            download = DownloadRequest(
                url=image.url, local_path=local_path, expected_md5=image.md5
            )
            downloads.append(download)
        self._conservator.files.download_many(downloads, no_meter=no_meter)

    def download_datasets(self, path, no_meter=False):
        """Clones and pulls all datasets in the collection."""
        fields = FieldsRequest()
        fields.include_field("name", "repository.master")
        datasets = self.get_datasets(fields=fields)
        for dataset in datasets:
            clone_path = os.path.join(path, dataset.name)
            lds = LocalDataset.clone(dataset, clone_path=clone_path)
            lds.download(no_meter=no_meter)
