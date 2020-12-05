"""
A Manager is simply a bundle of utilities for querying a specific type.
"""
import os

from FLIR.conservator.managers.searchable import SearchableTypeManager
from FLIR.conservator.types import Collection, Dataset, Project, Video, Image
from FLIR.conservator.util import upload_file


class VideoUploadException(Exception):
    pass


class CollectionManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Collection)

    def from_remote_path(self, path, make_if_no_exist=False, fields=None):
        return self._underlying_type.from_remote_path(self._conservator, path,  make_if_no_exist, fields)

    def create_root(self, name, fields=None):
        return self._underlying_type.create_root(self._conservator, name, fields)

    def create_from_parent_id(self, name, parent_id, fields=None):
        parent = self.from_id(parent_id)
        return parent.create_child(name, fields)

    def create_from_path(self, path, fields=None):
        return self.from_remote_path(path, make_if_no_exist=True, fields=fields)


class DatasetManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Dataset)

    def from_local_path(self, path="."):
        """Create a :class:`~FLIR.conservator.types.Dataset` from a `path`
        containing an ``index.json`` file."""
        return self._underlying_type.from_local_path(self._conservator, path)


class ProjectManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Project)

    def create(self, name, fields=None):
        self._underlying_type.create(self._conservator, name, fields=fields)


class VideoManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Video)

    def upload(self, file_path, collection=None, remote_name=None):
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


class ImagesManager(SearchableTypeManager):
    def __init__(self, conservator):
        super().__init__(conservator, Image)


