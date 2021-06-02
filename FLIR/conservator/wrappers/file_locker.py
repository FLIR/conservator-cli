import os

from FLIR.conservator.file_transfers import DownloadRequest, FileUploadException
from FLIR.conservator.wrappers import TypeProxy
from FLIR.conservator.wrappers.type_proxy import requires_fields


class FileLockerUploadException(Exception):
    """Raised if an exception occurs during a file-locker upload"""

    pass


class FileLockerType(TypeProxy):
    """
    Adds :func:`download_associated_files`, :func:`upload_associated_file`, :func:`remove_associated_file`

    Every FileLocker file is associated with a Conservator object, and the
    relevant mutations to create or remove such a file depend on object type.
    The subclass is responsible for specifying those mutations as
    'file_locker_gen_url' and 'file_locker_remove' members, and also an
    'id_type' member that names the id arg for those mutations (e.g.
    "dataset_id" or "video_id").

    Arguments and return values for the FileLocker mutations:
      create
      - args = parent_id, filename, and content_type
      - return = string signed_url, string url
      remove
      - args = parent_id, filename
      - return = instance of parent object type
    """

    file_locker_gen_url = None
    file_locker_remove = None
    id_type = None

    # Conservator doesn't seem to like "application/octet-stream" for Content-Type
    default_file_type = ""

    def _generate_file_locker_url(self, file_path, content_type):
        """
        Generate URL for uploading a file to Conservator as associated file of
        this FileLocker's parent object
        """
        filename = os.path.basename(file_path)
        mutation_args = {
            self.id_type: self.id,
            "filename": filename,
            "content_type": content_type,
        }
        result = self._conservator.query(self.file_locker_gen_url, **mutation_args)
        return result.signed_url

    @requires_fields("file_locker_files")
    def download_associated_files(self, path, no_meter=False):
        """Downloads associated files (from file locker) to
        ``associated_files/``."""
        path = os.path.join(path, "associated_files")
        os.makedirs(path, exist_ok=True)
        downloads = []

        for file in self.file_locker_files:
            local_path = os.path.join(path, file.name)
            download = DownloadRequest(url=file.url, local_path=local_path)
            downloads.append(download)
        self._conservator.files.download_many(downloads, no_meter=no_meter)

    def upload_associated_file(self, file_path, content_type=None):
        """
        Uploads file to Conservator as associated file of this FileLocker's
        parent object
        """
        if not content_type:
            content_type = self.default_file_type
        url = self._generate_file_locker_url(file_path, content_type)
        try:
            self._conservator.files.upload(url=url, local_path=file_path)
        except FileUploadException as e:
            raise FileLockerUploadException from e
        return True

    def remove_associated_file(self, filename):
        """
        Removes named file from set of associated files for this FileLocker's
        parent object
        """
        mutation_args = {self.id_type: self.id, "filename": filename}
        result = self._conservator.query(
            self.file_locker_remove,
            fields="id",
            **mutation_args,
        )
        return True
