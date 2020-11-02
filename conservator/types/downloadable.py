import json
import os

from conservator.types.type_proxy import TypeProxy
from conservator.util import download_file


class DownloadableAsset:
    def __init__(self, required_fields):
        self.required_fields = required_fields

    def download(self, instance, path, asset_names, **kwargs):
        raise NotImplementedError


class DownloadableType(TypeProxy):
    downloadable_assets = {}

    def download(self, path):
        raise NotImplementedError

    def download_assets(self, path, asset_names, **kwargs):
        requested_assets = []
        required_fields = ["name"]
        for asset_name in asset_names:
            asset = self.downloadable_assets.get(asset_name, None)
            if asset is None:
                raise NotImplementedError
            requested_assets.append(asset)
            required_fields.extend(asset.required_fields)

        self.populate(required_fields)
        path = os.path.join(path, self.name)

        for asset in requested_assets:
            asset.download(self, path, asset_names, **kwargs)


class SubtypeDownload(DownloadableAsset):
    """
    Calls :func:``DownloadableType.download`` on the children of an object.
    This can be used to download videos in a collection, frames in a video, etc.

    :param field_name: Specifies the name of the field that contains the subtypes IDs.
    :param field_type: The type of the subtype to instantiate.
    """
    def __init__(self, field_type, field_name):
        super().__init__([field_name])
        self.field_type = field_type
        self.field_name = field_name

    def download(self, instance, path, asset_names, **kwargs):
        for subtype_id in getattr(instance, self.field_name):
            subtype_instance = self.field_type.from_id(subtype_id)
            subtype_instance.download(path, **kwargs)


class RecursiveDownload(DownloadableAsset):
    """
    Calls :func:``DownloadableType.download`` on the children of an object.

    :param child_field_name: Specifies the name of the field that contains the child IDs.
    """
    def __init__(self, child_field_name="child_ids"):
        super().__init__([child_field_name])
        self.child_field_name = child_field_name

    def download(self, instance, path, asset_names, **kwargs):
        for child_id in getattr(instance, self.child_field_name):
            child_instance = instance.from_id(instance._conservator, child_id)
            child_instance.download_assets(path, asset_names, **kwargs)


class AssociatedFilesDownload(DownloadableAsset):
    """
    Downloads the associated files of an object, found in :prop:``file_locker_files``.
    """
    def __init__(self):
        super().__init__(["file_locker_files"])

    def download(self, instance, path, asset_names, **kwargs):
        path = os.path.join(path, "associated_files")
        os.makedirs(path, exist_ok=True)
        for file in instance.file_locker_files:
            download_file(path, file.name, file.url)


class VideosDownload(DownloadableAsset):
    pass

class ImagesDownload(DownloadableAsset):
    pass


class FieldAsJsonDownload(DownloadableAsset):
    def __init__(self, field):
        super().__init__([field])
        self.field = field
    
    def download(self, instance, path, asset_names, **kwargs):
        data = getattr(instance, self.field)
        file = os.path.join(path, self.field + ".json")
        with open(file) as f:
            json.dump(data, f)


class DatasetsFromCollectionDownload(DownloadableAsset):
    def __init__(self):
        super().__init__([])

    def download(self, instance, path, asset_names, **kwargs):
        for dataset in instance.get_datasets():
            dataset.download(path, **kwargs)
