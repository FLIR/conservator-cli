import logging
import multiprocessing
import os
import random
import time

from FLIR.conservator.config import Config
from FLIR.conservator.connection import ConservatorConnection
from FLIR.conservator.generated.schema import Query
from FLIR.conservator.managers import (
    CollectionManager,
    DatasetManager,
    ProjectManager,
    VideoManager,
    ImageManager,
)
from FLIR.conservator.util import base_convert, upload_file
from FLIR.conservator.wrappers import Video

logger = logging.getLogger(__name__)


class Conservator(ConservatorConnection):
    """
    :class:`Conservator` is the highest level class of this library. It will likely be the
    starting point for all queries and operations.

    You can get an instance using the default :class:`~FLIR.conservator.config.Config`:

    >>> Conservator.default()
    <Conservator at https://flirconservator.com>

    You can create also create an instance by passing any :class:`~FLIR.conservator.config.Config`
    object:

    >>> config = Config(my_email, my_key, "https://localhost:3000")
    >>> Conservator(config)
    <Conservator at https://localhost:3000>

    :param config: The :class:`~FLIR.conservator.config.Config` object to use for this connection.
    """

    def __init__(self, config):
        super().__init__(config)
        self.collections = CollectionManager(self)
        self.datasets = DatasetManager(self)
        self.projects = ProjectManager(self)
        self.videos = VideoManager(self)
        self.images = ImageManager(self)
        logger.debug(f"Created new Conservator with config '{config}'")

    def __repr__(self):
        return f"<Conservator at {self.config.url}>"

    def get_user(self):
        """Returns the User that the provided API token authorizes"""
        return self.query(Query.user)

    ID_CHARSET = "23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz"
    ID_CHARSET_SIZE = len(ID_CHARSET)
    ID_LENGTH = 17

    @staticmethod
    def generate_id():
        """
        Generate a new ID.

        The ID consists of ``ID_LENGTH`` characters from the ``ID_CHARSET``.
        The beginning of the ID is based on the current time, and the remaining
        characters are random.
        """
        t = time.time()
        time_digits = base_convert(Conservator.ID_CHARSET_SIZE, t)[::-1]
        id_ = [Conservator.ID_CHARSET[i] for i in time_digits]
        remaining_digits = Conservator.ID_LENGTH - len(id_)
        id_ += random.sample(Conservator.ID_CHARSET, remaining_digits)
        return "".join(id_)

    @staticmethod
    def default(save=True):
        """
        Returns a :class:`Conservator` using :meth:`Config.default() <FLIR.conservator.config.Config.default>`.
        """
        return Conservator(Config.default(save=save))

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
            collection = self.collections.from_id(collection)
        if collection is not None:
            video = collection.create_video(remote_name, fields="id")
        else:
            video = Video.create(self, remote_name, fields="id")

        upload_id = video.initiate_upload(remote_name)

        url = video.generate_signed_upload_url(upload_id)
        upload = upload_file(file_path, url)
        if not upload.ok:
            video.remove()
            raise MediaUploadException(
                f"Upload failed ({upload.status_code}: {upload.reason})"
            )
        completion_tag = upload.headers["ETag"]

        video.complete_upload(remote_name, upload_id, completion_tags=[completion_tag])
        video.trigger_processing()
        return video.id

    def get_media_instance_from_id(self, media_id, fields=None):
        """
        Returns a Video or Image object from an ID. These types are checked in
        this order, until :meth:`~FLIR.conservator.managers.type_manager.id_exists`
        returns `True`. If neither matches, an :class:`UnknownMediaIdException` is raised.
        """
        if self.videos.id_exists(media_id):
            media = self.videos.from_id(media_id)
            media.populate(fields)
            return media

        if self.images.id_exists(media_id):
            media = self.images.from_id(media_id)
            media.populate(fields)
            return media

        raise UnknownMediaIdException(f"The type of ID '{media_id}' could not be found")

    def is_uploaded_media_id_processed(self, media_id):
        """
        Return `True` if an ID returned by :meth:`~MediaTypeManager.upload` has
        been processed, and `False` otherwise.

        When media is uploaded, it begins processing as a video. It may turn into
        an image, requiring different queries. This method can be used to verify
        that an ID is done processing, and its type won't change in the future.
        """
        media = self.get_media_instance_from_id(media_id)
        media.populate("state")
        return media.state == "completed"

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

    def upload_many(self, upload_tuples, process_count=None):
        """
        Upload many files in parallel. Returns a list of the uploaded media IDs.

        :param upload_tuples: A list of `file_path`, `collection_id`, `remote_name` tuples
            that will be passed to :meth:`~MediaTypeManager.upload`.
        :param process_count: Number of concurrent upload processes. Passing `None`
            will use `os.cpu_count()`.
        """
        pool = multiprocessing.Pool(process_count)
        results = pool.starmap(self.upload, upload_tuples)
        return results

    def upload_many_to_collection(self, file_paths, collection, process_count=None):
        """
        Upload many files in parallel. Returns a list of the uploaded media IDs.

        :param file_paths: A list of `str` file paths to upload to `collection`. Alternatively,
            a list of `(str, str)` tuples holding pairs of `local_path`, `remote_name`. If `remote_name`
            is `None`, the local filename will be used.
        :param collection: The collection to upload media files to.
        :param process_count: Number of concurrent upload processes. Passing `None`
            will use `os.cpu_count()`.
        """
        if len(file_paths) == 0:
            return

        if isinstance(file_paths[0], str):
            file_paths = [(file_path, None) for file_path in file_paths]

        upload_tuples = [
            (file_path[0], collection.id, file_path[1]) for file_path in file_paths
        ]
        return self.upload_many(upload_tuples, process_count=process_count)


class MediaUploadException(Exception):
    """Raised if an exception occurs during a media upload"""

    pass


class ProcessingTimeoutError(TimeoutError):
    """
    Raised when the amount of time spent waiting for media to process exceeds
    the requested timeout.
    """

    pass


class UnknownMediaIdException(Exception):
    """
    Raised when a media ID cannot be resolved to a Video or Image.
    """

    pass
