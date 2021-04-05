"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
import glob
import json
import logging
import os

from FLIR.conservator.managers.media import MediaTypeManager
from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.managers.type_manager import AmbiguousIdentifierException
from FLIR.conservator.wrappers import (
    Collection,
    Dataset,
    Project,
    Video,
    Image,
)


logger = logging.getLogger(__name__)


class CollectionManager(SearchableTypeManager):
    metadata_subdir = "media_metadata"
    associated_files_subdir = "associated_files"

    def __init__(self, conservator):
        super().__init__(conservator, Collection)

    def from_string(self, string, fields="id"):
        """
        Returns a Collection with the given `fields` from a `string`.
        If the `string` contains any slashes, it is assumed to be a path,
        and :meth:`from_remote_path` is used. Otherwise, `from_id` is used.

        This is used for CLI commands to let users specify paths or ids when
        doing operations, and should be the preferred method for getting a Collection from
        any user-facing input.
        """
        if "/" in string:
            # slash cannot exist in an ID
            # this will throw InvalidRemotePathException if path cannot be found.
            return self.from_remote_path(
                path=string, make_if_no_exist=False, fields=fields
            )
        # this throws InvalidIdException is ID is invalid format
        collection = self.from_id(string)
        # this will throw InvalidIdException if the ID doesn't exist
        collection.populate(fields)
        return collection

    def from_remote_path(self, path, make_if_no_exist=False, fields=None):
        """
        Returns a collection at the specified `path`, with the specified `fields`.
        If `make_if_no_exist` is `True`, then collection(s) will be created to
        reach that path.
        """
        return self._underlying_type.from_remote_path(
            self._conservator, path, make_if_no_exist, fields
        )

    def create_root(self, name, fields=None):
        """
        Create a new root collection with the specified `name` and
        return it with the specified `fields`.
        """
        return self._underlying_type.create_root(self._conservator, name, fields)

    def create_from_parent_id(self, name, parent_id, fields=None):
        """
        Create a new child collection named `name`, under the parent collection with the
        given `parent_id`, and return it with the given `fields`.
        """
        parent = self.from_id(parent_id)
        return parent.create_child(name, fields)

    def create_from_remote_path(self, path, fields=None):
        """
        Return a new collection at the specified `path`, with the given `fields`,
        creating new collections as necessary.

        If the path already exists, raises :class:`RemotePathExistsException`.
        """
        return self._underlying_type.create_from_remote_path(
            self._conservator, path, fields=fields
        )

    def create_from_path(self, path, fields=None):
        """
        .. deprecated:: 1.1.0
            Use :meth:`create_from_remote_path` instead.
        """
        return self.create_from_remote_path(path, fields=fields)

    def upload(
        self,
        collection_id,
        path,
        video_metadata,
        associated_files,
        media,
        recursive,
        resume_media,
        max_retries,
    ):
        """
        Upload files under the specified `path` to given collection. `max_retries` only applies
        to media files (other types of files are usually small enough not to need them).
        """

        collection = self.from_id(collection_id)
        collection.populate(["name", "path"])

        # a couple of subdirs are special cases if present,
        # and anything starting with dot should be ignored
        child_names = os.listdir(path)
        if self.metadata_subdir in child_names:
            child_names.remove(self.metadata_subdir)
        if self.associated_files_subdir in child_names:
            child_names.remove(self.associated_files_subdir)
        child_names = [name for name in child_names if not name.startswith(".")]

        # split remaining into media files and child dirs
        child_paths = [os.path.join(path, name) for name in child_names]
        media_paths = list(filter(os.path.isfile, child_paths))
        subdir_paths = list(filter(os.path.isdir, child_paths))

        if media:
            logger.info("Uploading media to collection %s", collection.path)
            media_manager = MediaTypeManager(self._conservator)
            media_manager.upload_many_to_collection(
                media_paths, collection, resume=resume_media, max_retries=max_retries
            )

        if video_metadata:
            logger.info("Uploading metadata to collection %s", collection.path)
            metadata_glob = os.path.join(path, self.metadata_subdir, "*.json")
            metadata_paths = glob.glob(metadata_glob)
            for file_path in metadata_paths:
                logger.info("Upload metadata file %s", file_path)

                # find the media this file belongs to
                metadata = {}
                with open(file_path) as fp:
                    metadata = json.load(fp)
                media_id = metadata["videos"][0]["id"]

                try:
                    media = self._conservator.get_media_instance_from_id(media_id)
                    media.upload_metadata(file_path)
                # oops importing real exception UnknownMediaIdException causes import loop
                except:
                    logger.error(
                        "Skip metadata %s (media id=%s not found)", file_path, media_id
                    )

        if associated_files:
            logger.info("Uploading associated files to collection %s", collection.path)
            associated_files_dir = os.path.join(path, self.associated_files_subdir)
            associated_files_paths = os.listdir(associated_files_dir)
            for file_path in associated_files_paths:
                logger.info("Upload associated file %s", file_path)
                collection.upload_associated_file(file_path)

        if recursive:
            for subdir_path in subdir_paths:
                logger.info("Descending into subdir %s", subdir_path)
                name = os.path.basename(subdir_path)
                child_path = os.path.join(collection.path, name)
                child = self.create_from_path(child_path)
                self.upload(
                    child.id,
                    subdir_path,
                    video_metadata,
                    associated_files,
                    media,
                    recursive,
                    resume_media,
                    max_retries,
                )


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)

    def from_local_path(self, path="."):
        """Create a :class:`~FLIR.conservator.wrappers.Dataset` from a `path`
        containing an ``index.json`` file."""
        return self._underlying_type.from_local_path(self._conservator, path)

    def create(self, name, collections=None, fields=None):
        """
        Create a dataset with the given `name`, including the given `collections`, if specified.
        The dataset is returned with the requested `fields`.
        """
        return self._underlying_type.create(
            self._conservator, name, collections=collections, fields=fields
        )

    def from_string(self, string, fields="id"):
        """
        Returns a Dataset with the given `fields` from a `string`.
        If the `string` contains any slashes (for instance `/path/to/some/collection/dataset_name`),
        it is assumed to be a path, and the parent directory of the path will be fetched,
        and its datasets will be searched for an exact match on dataset name.

        Next, we check if `string` matches any single dataset name exactly using
        :meth:`~FLIR.conservator.managers.SearchableTypeManager.by_exact_name`.

        Otherwise, we assume `string` is an `ID`, and use :meth:`from_id`.

        This is used for CLI commands to let users specify paths or ids when
        doing operations, and should be the preferred method for getting a Dataset from
        any user-facing input.
        """
        if "/" in string:
            # start by path lookup
            parent_path = "/".join(string.split("/")[:-1])
            name = string.split("/")[-1]

            parent = self._conservator.collections.from_remote_path(
                path=parent_path, make_if_no_exist=False, fields="id"
            )

            # collection must contain dataset with exact name match
            datasets = list(parent.get_datasets(fields=fields).filtered_by(name=name))
            if len(datasets) == 1:
                return datasets[0]
            if len(datasets) > 1:
                raise AmbiguousIdentifierException(string)

        # if path fails, look for exact name
        datasets = list(self.by_exact_name(name=string, fields=fields))
        if len(datasets) == 1:
            return datasets[0]
        if len(datasets) > 1:
            raise AmbiguousIdentifierException(string)

        # if that fails, look by id
        # this throws InvalidIdException is ID is invalid format
        dataset = self.from_id(string)
        # this will throw InvalidIdException if the ID doesn't exist
        dataset.populate(fields)
        return dataset


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)

    def create(self, name, fields=None):
        """
        Create a new project with the given `name`, and return
        it with the specified `fields`.
        """
        return self._underlying_type.create(self._conservator, name, fields=fields)


class VideoManager(SearchableTypeManager, MediaTypeManager):
    def __init__(self, conservator):
        SearchableTypeManager.__init__(self, conservator, Video)
        MediaTypeManager.__init__(self, conservator)

    def from_string(self, string, fields="id"):
        """
        Returns a Video with the given `fields` from a `string`.
        If the `string` contains any slashes (for instance `/path/to/some/collection/video_name`),
        it is assumed to be a path, and the parent directory of the path will be fetched,
        and its videos will be searched for an exact match on dataset name.

        Next, we check if `string` matches any single video name exactly using
        :meth:`~FLIR.conservator.managers.SearchableTypeManager.by_exact_name`.

        Otherwise, we assume `string` is an `ID`, and use :meth:`from_id`.

        This is used for CLI commands to let users specify paths or ids when
        doing operations, and should be the preferred method for getting a Video from
        any user-facing input.
        """
        if "/" in string:
            # start by path lookup
            parent_path = "/".join(string.split("/")[:-1])
            name = string.split("/")[-1]

            parent = self._conservator.collections.from_remote_path(
                path=parent_path, make_if_no_exist=False, fields="id"
            )

            # collection must contain video with exact name match
            videos = list(parent.get_videos(fields=fields).filtered_by(name=name))
            if len(videos) == 1:
                return videos[0]
            if len(videos) > 1:
                raise AmbiguousIdentifierException(string)

        # if path fails, look for exact name
        videos = list(self.by_exact_name(name=string, fields=fields))
        if len(videos) == 1:
            return videos[0]
        if len(videos) > 1:
            raise AmbiguousIdentifierException(string)

        # if that fails, look by id
        video = self.from_id(string)
        # this will throw InvalidIdException if the ID doesn't exist
        video.populate(fields)
        return video


class ImageManager(SearchableTypeManager, MediaTypeManager):
    def __init__(self, conservator):
        SearchableTypeManager.__init__(self, conservator, Image)
        MediaTypeManager.__init__(self, conservator)

    def from_string(self, string, fields="id"):
        """
        Returns an Image with the given `fields` from a `string`.
        If the `string` contains any slashes (for instance `/path/to/some/collection/image_name`),
        it is assumed to be a path, and the parent directory of the path will be fetched,
        and its images will be searched for an exact match on dataset name.

        Next, we check if `string` matches any single image name exactly using
        :meth:`~FLIR.conservator.managers.SearchableTypeManager.by_exact_name`.

        Otherwise, we assume `string` is an `ID`, and use :meth:`from_id`.

        This is used for CLI commands to let users specify paths or ids when
        doing operations, and should be the preferred method for getting an Image from
        any user-facing input.
        """
        if "/" in string:
            # start by path lookup
            parent_path = "/".join(string.split("/")[:-1])
            name = string.split("/")[-1]

            parent = self._conservator.collections.from_remote_path(
                path=parent_path, make_if_no_exist=False, fields="id"
            )

            # collection must contain video with exact name match
            images = list(parent.get_images(fields=fields).filtered_by(name=name))
            if len(images) == 1:
                return images[0]
            if len(images) > 1:
                raise AmbiguousIdentifierException(string)

        # if path fails, look for exact name
        images = list(self.by_exact_name(name=string, fields=fields))
        if len(images) == 1:
            return images[0]
        if len(images) > 1:
            raise AmbiguousIdentifierException(string)

        # if that fails, look by id
        # this throws InvalidIdException is ID is invalid format
        image = self.from_id(string)
        # this will throw InvalidIdException if the ID doesn't exist
        image.populate(fields)
        return image
