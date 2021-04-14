import json
import os

from FLIR.conservator.file_transfers import FileUploadException
from FLIR.conservator.wrappers import TypeProxy
from FLIR.conservator.wrappers.type_proxy import requires_fields


class MetadataUploadException(Exception):
    """Raised if an exception occurs during a metadata upload"""

    pass


class MetadataType(TypeProxy):
    """
    Adds :func:`download_metadata` and :func:`upload_metadata`

    Every Metadata file belongs to a parent, and the relevant mutations to
    create such a file depend on parent type. The parent object's
    class is responsible for specifying the mutation as 'metadata_gen_url'
    and 'metadata_confirm' members, and also an 'id_type' member that names
    the id arg for those mutations (e.g. "dataset_id" or "video_id").

    Arguments and return values for the Metadata mutations:
      create
      - args = parent_id, filename, and content_type
      - return = string signed_url, string url
      confirm
      - args = parent_id, signed_url
      - return = boolean success
    """

    metadata_gen_url = None
    metadata_confirm_url = None
    id_type = None

    # Conservator doesn't seem to like "application/octet-stream" for Content-Type
    default_file_type = ""

    def _generate_metadata_url(self, file_path, content_type):
        """
        Generate URL for uploading a file to Conservator as metadata of
        this Metadata's parent object
        """
        filename = os.path.basename(file_path)
        mutation_args = {
            self.id_type: self.id,
            "filename": filename,
            "content_type": content_type,
        }
        result = self._conservator.query(self.metadata_gen_url, **mutation_args)
        return result

    def _confirm_metadata_upload(self, url):
        """
        Confirm metadata upload to given URL is complete
        """
        mutation_args = {
            "id": self.id,
            "url": url,
        }
        result = self._conservator.query(self.metadata_confirm_url, **mutation_args)
        return result

    @requires_fields("metadata", "filename")
    def download_metadata(self, path):
        """
        Downloads the `metadata` field to `path/filename.json`,
        where `filename` is the media's filename.
        """
        json_data = json.loads(self.metadata)
        json_file = ".".join(self.filename.split(".")[:-1]) + ".json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(",", ": "))

    def upload_metadata(self, file_path, content_type=None):
        """
        Uploads file to Conservator as associated file of this Metadata's
        parent object
        """
        if not content_type:
            content_type = self.default_file_type
        url = self._generate_metadata_url(file_path, content_type)
        try:
            self._conservator.files.upload(url=url.signed_url, local_path=file_path)
        except FileUploadException as e:
            raise MetadataUploadException from e
        result = self._confirm_metadata_upload(url.url)
        return result
