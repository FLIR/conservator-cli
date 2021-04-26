import multiprocessing
import os
import logging

import requests
import tqdm

from FLIR.conservator.util import md5sum_file

logger = logging.getLogger(__name__)


class DownloadRequest:
    """
    For use with :meth:`ConservatorFileTransfers.download_many`.

    A request to download from `url` to `local_path`. If
    `expected_md5` is given, check the file doesn't already exist
    with the correct hash before downloading.
    """

    def __init__(self, url, local_path, expected_md5=None):
        self.url = url
        self.local_path = local_path
        self.expected_md5 = expected_md5


class UploadRequest:
    """
    For use with :meth:`ConservatorFileTransfers.upload_many`.

    A request to upload `local_path` to `url`.
    """

    def __init__(self, url, local_path):
        self.url = url
        self.local_path = local_path


class FileTransferException(Exception):
    """
    Something went wrong when uploading or downloading a file.
    """


class FileDownloadException(FileTransferException):
    """
    Something went wrong when downloading a file.
    """


class FileUploadException(FileTransferException):
    """
    Something went wrong when uploading a file.
    """


class ConservatorFileTransfers:
    """
    Bundles methods for uploading and downloading files to Conservator.

    These methods cannot be standalone utilities because in some deployments
    URLs will be relative to the base Conservator URL. Therefore, all download
    and upload operations need to have a reference to the Conservator instance.
    """

    def __init__(self, conservator):
        self._conservator = conservator

    def full_url(self, url):
        """
        Converts a `url` from Conservator into a full URL (protocol, domain, etc.)
        that can be used for uploading or downloading.
        """
        if url.startswith("/"):
            return self._conservator.get_url() + url
        return url

    def download_if_missing(self, url, local_path, expected_md5, no_meter=False):
        """
        Check that a file exists at `local_path` with the `expected_md5` hash. If it
        doesn't, download it from `url`.
        """
        directory, file = os.path.split(local_path)
        if os.path.exists(local_path):
            local_md5 = md5sum_file(local_path)
            if local_md5 == expected_md5:
                logger.info(f"Skip {file} (already downloaded)")
                return True
        return self.download(url, local_path, no_meter=no_meter)

    def download(self, url, local_path, no_meter=False):
        """
        Download the file from Conservator `url` to the `local_path`.
        """
        directory, file = os.path.split(local_path)
        os.makedirs(directory, exist_ok=True)
        url = self.full_url(url)

        logger.debug(f"Downloading {file} from {url}")
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            if not response.ok:
                raise FileDownloadException(url)
        except requests.exceptions.ConnectionError as e:
            raise FileDownloadException(url) from e

        size = int(response.headers.get("content-length", 0))
        progress = tqdm.tqdm(
            total=size, unit="B", unit_scale=True, unit_divisor=1024, disable=no_meter
        )
        progress.set_description(f"Downloading {file}")
        chunk_size = 1024 * 1024

        try:
            with open(local_path, "wb") as fd:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    progress.update(len(chunk))
                    fd.write(chunk)
        except BaseException as e:  # BaseException includes KeyboardInterrupt
            # To avoid partial downloads:
            if os.path.exists(local_path):
                os.remove(local_path)

            raise FileDownloadException(url) from e
        finally:
            progress.close()
        return response

    def _do_download_request(self, download_request):
        try:
            if download_request.expected_md5 is not None:
                return self.download_if_missing(
                    url=download_request.url,
                    local_path=download_request.local_path,
                    expected_md5=download_request.expected_md5,
                    no_meter=True,
                )
            return self.download(
                url=download_request.url,
                local_path=download_request.local_path,
                no_meter=True,
            )
        except FileDownloadException:
            # This is called from multiprocessing context, errors should not be raised.
            logger.warning(f"Encountered FileDownloadException with {download_request}")
            return False

    def _do_upload_request(self, upload_request):
        try:
            return self.upload(
                url=upload_request.url, local_path=upload_request.local_path
            )
        except FileUploadException:
            # This is called from multiprocessing context, errors should not be raised.
            logger.warning(f"Encountered FileUploadException with {upload_request}")
            return False

    def upload(self, url, local_path):
        """
        Upload the file at `local_path` to Conservator `url`.
        """
        url = self.full_url(url)
        path = os.path.abspath(local_path)
        logger.info(f"Uploading '{path}'")
        with open(path, "rb") as f:
            response = requests.put(url, f)
        if not response.ok:
            raise FileUploadException(url)
        logger.info(f"Completed upload of '{path}'")
        return response

    def download_many(self, downloads, process_count=None, no_meter=False):
        """
        Download a list of `DownloadRequest` in parallel.

        :param downloads: The `list` of `DownloadRequest` to download.
        :param process_count: The number of concurrent downloads. If `None`, uses
            ``os.cpu_count()``.
        :param no_meter: If `True`, hide the progress bar.
        """
        with multiprocessing.Pool(process_count) as pool:
            progress = tqdm.tqdm(
                iterable=pool.imap(self._do_download_request, downloads),
                desc="Downloading files",
                total=len(downloads),
                disable=no_meter,
            )
            # We need to consume the results as they're output to update the progress bar. We use list.
            return list(progress)

    def upload_many(self, uploads, process_count=None, no_meter=False):
        """
        Upload a list of `UploadRequest` in parallel.

        :param uploads: The `list` of `UploadRequest` to download.
        :param process_count: The number of concurrent uploads. If `None`, uses
            ``os.cpu_count()``.
        :param no_meter: If `True`, hide the progress bar.
        """
        with multiprocessing.Pool(process_count) as pool:
            progress = tqdm.tqdm(
                iterable=pool.imap(self._do_upload_request, uploads),
                desc="Uploading files",
                total=len(uploads),
                disable=no_meter,
            )
            # We need to consume the results as they're output to update the progress bar. We use list.
            return list(progress)
