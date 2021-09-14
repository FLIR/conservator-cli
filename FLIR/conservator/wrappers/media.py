import enum
import os
import traceback
from dataclasses import dataclass

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import Mutation, Query
from FLIR.conservator.util import md5sum_file
from FLIR.conservator.wrappers import QueryableType
from FLIR.conservator.wrappers.file_locker import FileLockerType
from FLIR.conservator.wrappers.metadata import MetadataType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class MediaUploadException(Exception):
    """Raised if an exception occurs during a media upload"""

    pass


class MediaCompare(enum.Enum):
    """Results of comparing local file and Conservator file"""

    MISMATCH = 0
    MATCH = 1

    def ok(self):
        return self.name == "MATCH"


@dataclass
class MediaUploadRequest:
    """Tracks inputs and results of a media upload"""

    file_path: str
    collection_id: str = ""
    remote_name: str = ""
    complete: bool = False
    media_id: str = ""
    error_message: str = ""

    def __eq__(self, other):
        # ignore status fields when deciding on a match
        match = False
        if isinstance(other, MediaUploadRequest):
            match = (
                self.file_path == other.file_path
                and self.collection_id == other.collection_id
                and self.remote_name == other.remote_name
            )
        return match


class MediaType(QueryableType, FileLockerType, MetadataType):
    """
    A media type is an image or a video. It can be uploaded (using
    :meth:`~FLIR.conservator.managers.media.MediaTypeManager.upload`)
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

    @staticmethod
    def verify_md5(local_path, expected_md5):
        """
        Helper for Video and Image md5sum comparisons, each of which
        track md5sum in Conservator but not in the same field
        """
        local_md5 = md5sum_file(local_path)
        if local_md5 == expected_md5:
            return MediaCompare.MATCH
        return MediaCompare.MISMATCH

    @requires_fields("md5")
    def compare(self, local_path):
        """
        Use md5 checksums to compare media contents to local file

        Returns result as MediaCompare object

        :param local_path: Path to local copy of file for comparison with remote.
        """
        return MediaType.verify_md5(local_path, self.md5)

    def get_annotations(self, fields=None):
        """
        Returns a list of the media's annotations with the specified `fields`.
        """
        return self._conservator.query(
            Query.annotations_by_video_id, fields=fields, id=self.id
        )

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
            fields=fields,
            id=self.id,
            metadata_url=metadata_url,
            should_notify=should_notify,
            should_object_detect=should_object_detect,
            new_upload=True,
        )

    def _generate_signed_upload_url(self, upload_id, part_number=1):
        """
        Returns a signed url for uploading a video or image.

        :param upload_id: An upload id returned by :func:`initiate_upload`.
        :param part_number: The part number if uploading a multipart video.
        """
        result = self._conservator.query(
            Mutation.generate_signed_multipart_video_upload_url,
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
            video_id=self.id,
            filename=filename,
            upload_id=upload_id,
            completion_tags=completion_tags,
        )
        assert result is True
        return result

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
            filename=filename,
            collection_id=collection_id,
        )
        # We want to re-wrap here, so we don't get Video-specific methods
        # on something that might become an Image...
        return MediaType(conservator, result)

    @staticmethod
    def upload(conservator, upload_request):
        """
        Upload a new media object based on info in :class:`MediaUploadRequest` object:
        * from a local `file_path`
        * to conservator name `remote_name`
        * as member of `collection` if given, otherwise added to no collection (orphan)

        Conservator Images have separate queries than Videos, but they do not get
        their own mutations, e.g. they are treated as "Videos" in the upload process.
        In fact, an uploaded media file is treated by Conservator server as a video
        until file processing has finished; if it turned out to be an image type
        (e.g. jpeg) then it will disappear from Videos and appear under Images.

        Returns updated MediaUploadRequest, which contains ID of the created media object (may be a
        Video ID or an Image ID) or else an error message if something went wrong.
        """
        assert isinstance(upload_request, MediaUploadRequest)
        file_path = upload_request.file_path
        remote_name = upload_request.remote_name
        collection_id = upload_request.collection_id or None

        file_path = os.path.expanduser(file_path)
        assert os.path.isfile(file_path)
        if remote_name is None:
            remote_name = os.path.split(file_path)[-1]

        media = None
        try:
            media = MediaType._create(conservator, remote_name, collection_id)
            upload_id = media._initiate_upload(remote_name)

            url = media._generate_signed_upload_url(upload_id)
            response = conservator.files.upload(url=url, local_path=file_path)
            completion_tag = response.headers["ETag"]

            media._complete_upload(
                remote_name, upload_id, completion_tags=[completion_tag]
            )
            media._trigger_processing()

            upload_request.complete = True
            upload_request.error_message = ""
            upload_request.media_id = media.id
        except Exception as e:
            if media:
                # clean up partial upload if possible
                try:
                    media.remove()
                except Exception:
                    pass

            upload_request.complete = False
            upload_request.error_message = traceback.format_exc()

        return upload_request

    @requires_fields("url", "filename", "md5")
    def download(self, path, no_meter=False):
        """Download media to `path`."""
        local_path = os.path.join(path, self.filename)
        self._conservator.files.download_if_missing(
            url=self.url,
            local_path=local_path,
            expected_md5=self.md5,
            no_meter=no_meter,
        )

    def remove(self):
        """
        Remove a video or image from conservator. Note that this is a permanent action that will
        remove it from **all** collections.
        """
        return self._conservator.query(
            Mutation.remove_video,
            id=self.id,
        )

    def get_frame_by_index(self, index, fields=None):
        """
        Returns a single frame at a specific `index` in the video.
        """
        frames = self._query_frames(frame_index=index, fields=fields)
        if len(frames) != 1:
            raise IndexError(f"Invalid frame index: {index}")
        return frames[0]

    def get_all_frames_paginated(self, fields=None):
        """
        Yields all frames in the video, 15 at a time, using
        :meth:`get_paginated_frames`.

        This is only useful if you're dealing with very long videos
        and want to paginate frames yourself. If the video is short,
        you could just use ``populate("frames")`` to get all frames.
        """
        start = 0
        while True:
            frames = self._paginated_frames(start, fields=fields)
            yield from frames
            # frame pagination size is hard-coded to 15 in conservator
            if len(frames) < 15:
                break
            start += 15

    def _paginated_frames(self, start_index=0, fields=None):
        """
        Returns 15 frames, starting with `start_index`.
        """
        return self._query_frames(start_frame_index=start_index, fields=fields)

    def _query_frames(self, start_frame_index=None, frame_index=None, fields=None):
        fields = FieldsRequest.create(fields)

        video_fields = {
            "frames": {
                "start_frame_index": start_frame_index,
                "frame_index": frame_index,
            }
        }
        for path, value in fields.paths.items():
            new_path = "frames." + path
            video_fields[new_path] = value

        video = self._conservator.query(
            query=self.by_id_query,
            fields=video_fields,
            id=self.id,
        )
        return video.frames
