import os

from FLIR.conservator.generated.schema import Mutation
from FLIR.conservator.util import download_file
from FLIR.conservator.util import upload_file
from FLIR.conservator.wrappers import QueryableType
from FLIR.conservator.wrappers.file_locker import FileLockerType
from FLIR.conservator.wrappers.metadata import MetadataType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class MediaUploadException(Exception):
    """Raised if an exception occurs during a media upload"""

    pass


class MediaType(QueryableType, FileLockerType, MetadataType):
    """
    A media type is an image or a video. It can be uploaded (using
    :meth:``FLIR.conservator.managers.media.MediaTypeManager.upload``)
    or downloaded.
    """

    # name of id field in mutations when not simply 'id'
    id_type = "video_id"

    # file-locker operations
    file_locker_gen_url = Mutation.generate_signed_file_locker_upload_url
    file_locker_remove = Mutation.remove_file_locker_file

    # metadata operations
    metadata_gen_url = Mutation.generate_signed_metadata_upload_url
    metadata_confirm_url = Mutation.mark_annotation_as_uploaded

    def _trigger_processing(
        self,
        metadata_url=None,
        should_notify=False,
        should_object_detect=True,
        fields=None,
    ):
        """
        Trigger processing on a recently uploaded video or image.
        """
        return self._conservator.query(
            Mutation.process_video,
            operation_base=Mutation,
            fields=fields,
            id=self.id,
            metadata_url=metadata_url,
            should_notify=should_notify,
            should_object_detect=should_object_detect,
        )

    def _generate_signed_upload_url(self, upload_id, part_number=1):
        """
        Returns a signed url for uploading a video or image.

        :param upload_id: An upload id returned by :func:`initiate_upload`.
        :param part_number: The part number if uploading a multipart video.
        """
        result = self._conservator.query(
            Mutation.generate_signed_multipart_video_upload_url,
            operation_base=Mutation,
            part_number=part_number,
            upload_id=upload_id,
            video_id=self.id,
        )
        return result

    def _initiate_upload(self, filename):
        """
        Initiate an upload to conservator with a remote `filename`,
        returning a new `upload_id`.
        """
        upload_id = self._conservator.query(
            Mutation.initiate_video_upload,
            operation_base=Mutation,
            video_id=self.id,
            filename=filename,
        )
        return upload_id

    def _complete_upload(self, filename, upload_id, completion_tags=None):
        """
        Complete an upload to conservator, after having uploaded the video to
        the url given by :func:`generate_signed_upload_url`.

        :param filename: The name of the video or image.
        :param upload_id: An upload id returned by :func:`initiate_upload`.
        :param completion_tags: An optional list of completion tags, typically the ``ETag``
            headers from any S3 uploads.
        """
        if completion_tags is None:
            completion_tags = []
        result = self._conservator.query(
            Mutation.complete_video_upload,
            operation_base=Mutation,
            video_id=self.id,
            filename=filename,
            upload_id=upload_id,
            completion_tags=completion_tags,
        )
        assert result is True

    @staticmethod
    def _create(conservator, filename, collection_id=None):
        """
        Create a new video or image with the given `filename`. The file is
        added under the collection with the given `collection_id` if
        specified, otherwise it is added to no collection (orphan video or
        image).
        """
        result = conservator.query(
            Mutation.create_video,
            operation_base=Mutation,
            filename=filename,
            collection_id=collection_id,
        )
        return MediaType(conservator, result)

    @staticmethod
    def upload(conservator, file_path, collection=None, remote_name=None):
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

        parent_id = None
        if collection is not None:
            parent_id = collection.id
        media = MediaType._create(conservator, remote_name, parent_id)

        upload_id = media._initiate_upload(remote_name)

        url = media._generate_signed_upload_url(upload_id)
        upload = upload_file(file_path, url)
        if not upload.ok:
            media.remove()
            raise MediaUploadException(
                f"Upload failed ({upload.status_code}: {upload.reason})"
            )
        completion_tag = upload.headers["ETag"]

        media._complete_upload(remote_name, upload_id, completion_tags=[completion_tag])
        media._trigger_processing()
        return media.id

    @requires_fields("url", "filename")
    def download(self, path, no_meter=False):
        """Download video to ``path``."""
        download_file(path, self.filename, self.url, no_meter=no_meter)

    def remove(self):
        """
        Remove a video or image from conservator. Note that this is a permanent action that will
        remove it from **all** collections.
        """
        return self._conservator.query(
            Mutation.remove_video, operation_base=Mutation, id=self.id
        )
