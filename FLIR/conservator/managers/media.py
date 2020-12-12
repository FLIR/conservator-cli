import os

from FLIR.conservator.types import Video
from FLIR.conservator.util import upload_file


class MediaUploadException(Exception):
    """Raised if an exception occurs during a media upload"""
    pass


class MediaTypeManager:
    def __init__(self, conservator):
        self._conservator = conservator

    def upload(self, file_path, collection=None, remote_name=None):
        """
        Upload a new media object from a local `file_path`, with the specified
        `remote_name`. It is added to `collection` if given, otherwise it is
        added to no collection (orphan).

        Conservator Images have separate queries than Videos, but they do not get
        their own mutations, e.g. they are treated as "Videos" in the upload process.
        In fact, an uploaded media file is treated by Conservator server as a video
        until file processing has finished; if it turned out to be an image type
        (e.g. jpeg) then it will disappear from Videos and appear under Images.

        Returns the ID of the created media object. Note, that it may be a Video ID
        or an Image ID.
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
            raise MediaUploadException(f"Upload failed ({upload.status_code}: {upload.reason})")
        completion_tag = upload.headers['ETag']

        video.complete_upload(remote_name, upload_id, completion_tags=[completion_tag])
        video.trigger_processing()
        return video.id
