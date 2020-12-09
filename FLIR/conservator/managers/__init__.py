"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
import os

from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.types import Collection, Dataset, Project, Video, Image
from FLIR.conservator.util import upload_file


class VideoUploadException(Exception):
    """Raised if an exception occurs during a video upload"""
    pass


class CollectionManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)

    def from_remote_path(self, path, make_if_no_exist=False, fields=None):
        """
        Returns a collection at the specified `path`, with the specified `fields`.
        If `make_if_no_exist` is `True`, then collection(s) will be created to
        reach that path.
        """
        return self._underlying_type.from_remote_path(self._conservator, path,  make_if_no_exist, fields)

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

    def create_from_path(self, path, fields=None):
        """
        Return a new collection at the specified `path`, with the given `fields`,
        creating new collections as necessary.  Uses :func:`from_remote_path` with
        `make_if_no_exist=True`.
        """
        return self.from_remote_path(path, make_if_no_exist=True, fields=fields)


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)

    def from_local_path(self, path="."):
        """Create a :class:`~FLIR.conservator.types.Dataset` from a `path`
        containing an ``index.json`` file."""
        return self._underlying_type.from_local_path(self._conservator, path)

    def create(self, name, collections=None, fields=None):
        """
        Create a dataset with the given `name`, including the given `collections`, if specified.
        The dataset is returned with the requested `fields`.
        """
        return self._underlying_type.create(self._conservator, name, collections=collections, fields=fields)


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)

    def create(self, name, fields=None):
        """
        Create a new project with the given `name`, and return
        it with the specified `fields`.
        """
        self._underlying_type.create(self._conservator, name, fields=fields)


class VideoManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Video)

    def upload(self, file_path, collection=None, remote_name=None):
        """
        Upload a new video from a local `file_path`, with the specified
        `remote_name`. The video is added to `collection` if given,
        otherwise it is added to no collection (orphan video).
        
        Returns the created :class:`~FLIR.conservator.types.video.Video`.
        """
        file_path = os.path.expanduser(file_path)
        assert os.path.isfile(file_path)
        if remote_name is None:
            remote_name = os.path.split(file_path)[-1]

        if collection is not None:
            video = collection.create_video(remote_name, fields="id")
        else:
            video = Video.create(self._conservator, remote_name, fields="id")

        upload_id = video.initiate_upload(remote_name)

        url = video.generate_signed_upload_url(upload_id)
        upload = upload_file(file_path, url)
        if not upload.ok:
            video.remove()
            raise VideoUploadException(f"Upload failed ({upload.status_code}: {upload.reason})")
        completion_tag = upload.headers['ETag']

        video.complete_upload(remote_name, upload_id, completion_tags=[completion_tag])
        video.trigger_processing()
        return video


class ImageManager(VideoManager):
    """
    Conservator Images have separate queries than Videos, but they do not get 
    their own mutations, e.g. they are treated as "Videos" in the upload process.
    In fact, an uploaded media file is treated by Conservator server as a video
    until file processing has finished; if it turned out to be an image type
    (e.g. jpeg) then it will disappear from Videos and appear under Images.
    """
    def __init__(self, conservator):
        super(VideoManager, self).__init__(conservator, Image)


