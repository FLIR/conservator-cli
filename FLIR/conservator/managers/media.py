import functools
import logging
import multiprocessing
import os
import time

from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.managers.type_manager import AmbiguousIdentifierException
from FLIR.conservator.wrappers.media import (
    MediaType,
    MediaUploadRequest,
    MediaUploadException,
)
from FLIR.conservator.wrappers.queryable import InvalidIdException

logger = logging.getLogger(__name__)


class ProcessingTimeoutError(TimeoutError):
    """
    Raised when the amount of time spent waiting for media to process exceeds
    the requested timeout.
    """

    pass


class MediaTypeManager:
    """
    Base class for media type managers.
    """

    def __init__(self, conservator):
        self._conservator = conservator

    def from_path(self, string, fields="id"):
        if "/" not in string:
            return None

        # start by path lookup
        parent_path = "/".join(string.split("/")[:-1])
        name = string.split("/")[-1]

        parent = self._conservator.collections.from_remote_path(
            path=parent_path, make_if_no_exist=False, fields="id"
        )

        # look inside parent for media with exact name match
        fields = FieldsRequest.create(fields)
        fields.include_field("name")
        media = list(parent.get_media(fields=fields, search_text="name:" + name))
        media = [m for m in media if m.name == name]
        if len(media) == 1:
            return media[0]
        if len(media) > 1:
            raise AmbiguousIdentifierException(string)
        return None

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

        :param file_path: The local file path to upload.
        :param collection: If specified, the Collection object, or `str` Collection ID to
            upload the media to. If not specified, the media is not uploaded to any
            specific collection (orphan).
        :param remote_name: If given, the remote name of the media. Otherwise, the local file
            name is used.
        """
        file_path = os.path.expanduser(file_path)
        assert os.path.isfile(file_path)
        if remote_name is None:
            remote_name = os.path.split(file_path)[-1]

        if isinstance(collection, str):
            collection_id = collection
        elif collection is not None:
            collection_id = collection.id
        else:
            collection_id = None

        upload_request = MediaUploadRequest(
            file_path=file_path, collection_id=collection_id, remote_name=remote_name
        )
        result = MediaType.upload(self._conservator, upload_request)
        if not result.complete:
            raise MediaUploadException(result.error_message)

        return result.media_id

    def is_uploaded_media_id_processed(self, media_id):
        """
        Return `True` if an ID returned by :meth:`~MediaTypeManager.upload` has
        been processed, and `False` otherwise.

        When media is uploaded, it begins processing as a video. It may turn into
        an image, requiring different queries. This method can be used to verify
        that an ID is done processing, and its type won't change in the future.
        """
        try:
            media = self._conservator.get_media_instance_from_id(media_id)
            media.populate("state")
            return media.state == "completed"
        except InvalidIdException:
            # If media changes types between get_instance() and populate()
            return False

    def _wait_for_single_processing(self, media_id, check_frequency_seconds):
        while not self.is_uploaded_media_id_processed(media_id):
            logger.debug(f"Media with id='{media_id}' is not processed yet")
            time.sleep(check_frequency_seconds)
        logger.info(f"Media with id='{media_id}' is processed!")
        return True

    def wait_for_processing(
        self, media_ids, timeout_seconds=600, check_frequency_seconds=5
    ):
        """
        Wait for an id, or list of ids, to complete processing.

        :param media_ids: A single `str` media ID, or a list of media ID to test.
        :param timeout_seconds: A maximum amount of time to wait.
        :param check_frequency_seconds: How long to wait between checks.
        """
        if isinstance(media_ids, str):
            media_ids = [media_ids]

        pool = multiprocessing.Pool()
        args = [(media_id, check_frequency_seconds) for media_id in media_ids]
        results = pool.starmap_async(self._wait_for_single_processing, args)
        try:
            processed = results.get(timeout=timeout_seconds)
            logger.debug(f"All media process checks returned, checking success")
            assert all(processed)
        except multiprocessing.TimeoutError:
            logger.debug(f"Media processing check timed out!")
            raise ProcessingTimeoutError()

    def _upload_many(self, upload_requests, process_count=None, max_retries=-1):
        """
        Upload many files in parallel. Returns the ids for media that were
        successfully uploaded (failed uploads will be logged as warning).

        :param upload_requests: A list of :class:`MediaUploadRequest` objects
            that will be passed to :meth:`~MediaTypeManager.upload`.
        :param process_count: Number of concurrent upload processes. Passing `None`
            will use `os.cpu_count()`.
        :param max_retries: maximum number of times upload will be attempted again
            for a file, if the initial attempt to upload that file fails. Value less
            than zero is interpreted as infinite retries.
        """
        pool = multiprocessing.Pool(process_count)
        upload_func = functools.partial(
            MediaType.upload, self._conservator
        )  # pass in conservator instance
        pending_uploads = list(upload_requests)
        complete_uploads = []

        tries = 0
        while pending_uploads:
            if max_retries >= 0 and tries > max_retries:
                logger.info("Ran out of retries, giving up")
                break

            logger.info("Upload attempt #%d", tries)
            results = pool.map(upload_func, pending_uploads)
            for upload in results:
                if upload.complete:
                    complete_uploads.append(upload)
                    pending_uploads.remove(upload)
                else:
                    logger.warning(
                        "Failed attempt to upload %s: %s",
                        upload.file_path,
                        upload.error_message,
                    )
            tries += 1

        if pending_uploads:
            file_list = [upload.file_path for upload in pending_uploads]
            logger.warning("Following files failed to upload: %s", file_list)

        media_ids = [upload.media_id for upload in complete_uploads]
        return media_ids

    def _clean_upload_list(self, file_paths, collection):
        """
        Clean up list of files prior to performing upload

        Side effects:
        * deletes remote file from Conservator if only partially uploaded
        * removes remote file from Conservator folder if complete but differs from local copy

        Returns list of files that need upload (anything from input list that did not match
          perfectly between local and remote copies)

        :param file_paths: List of `(str, str)` tuples holding pairs of `local_path`, `remote_name`.
            If `remote_name` is `None`, the local filename will be used.
        :param collection: The collection to which given files will later be uploaded.
        """
        redo_upload_paths = file_paths
        collection.populate("path")
        # iterate copy of list since items might be removed
        for path in list(file_paths):
            (local_path, remote_name) = path
            if remote_name is None:
                remote_name = os.path.split(local_path)[-1]
            remote_path = "/".join((collection.path, remote_name))
            media = self.from_path(remote_path, fields="state")
            if media:
                if media.state == "uploading":
                    # remove partially uploaded files from Conservator,
                    # leave on list to try uploading
                    logger.info("Removing incomplete upload of '%s'", remote_path)
                    media.remove()
                else:
                    if media.compare(local_path).ok():
                        # perfectly matching file,
                        # don't need to upload again
                        logger.info("File '%s' was already uploaded", remote_path)
                        redo_upload_paths.remove(path)
                    else:
                        # remove unmatching file from Conservator folder,
                        # leave on list to try uploading
                        logger.info("Unlinking file '%s' from folder", remote_path)
                        collection.remove_media(media.id)
        return redo_upload_paths

    def upload_many_to_collection(
        self, file_paths, collection, process_count=None, resume=False, max_retries=-1
    ):
        """
        Upload many files in parallel. Returns a list of the uploaded media IDs.

        :param file_paths: A list of `str` file paths to upload to `collection`. Alternatively,
            a list of `(str, str)` tuples holding pairs of `local_path`, `remote_name`. If `remote_name`
            is `None`, the local filename will be used.
        :param collection: The collection to upload media files to.
        :param process_count: Number of concurrent upload processes. Passing `None`
            will use `os.cpu_count()`.
        :param resume: Whether to check first if file was previously uploaded.
        :param max_retries: max number of upload retries per file in case of network errors.
        """
        if len(file_paths) == 0:
            return

        if isinstance(file_paths[0], str):
            file_paths = [(file_path, None) for file_path in file_paths]

        if resume:
            file_paths = self._clean_upload_list(file_paths, collection)

        upload_requests = [
            MediaUploadRequest(file_path[0], collection.id, file_path[1])
            for file_path in file_paths
        ]
        return self._upload_many(
            upload_requests, process_count=process_count, max_retries=max_retries
        )
