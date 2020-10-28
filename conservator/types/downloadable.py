from conservator.types.type_proxy import TypeProxy


class DownloadableAsset:
    def __init__(self, required_fields):
        self.required_fields = required_fields

    def download(self, instance, path, asset_names, **kwargs):
        raise NotImplementedError


class DownloadableType(TypeProxy):
    downloadable_assets = {}

    def download(self):
        raise NotImplementedError

    def download_assets(self, path, asset_names, **kwargs):
        requested_assets = []
        required_fields = []
        for asset_name in asset_names:
            asset = self.downloadable_assets.get(asset_name, None)
            if asset is None:
                raise NotImplementedError
            requested_assets.append(asset)
            required_fields.extend(asset.required_fields)

        self.populate(required_fields)

        for asset in self.downloadable_assets:
            asset.download_assets(self, path, asset_names, **kwargs)




class RecursiveDownload(DownloadableAsset):
    """
    Calls :func:``DownloadableType.download`` on the children of an object.

    :param child_field_name: Specifies the name of the field that contains the child IDs.
    """
    def __init__(self, child_field_name="children"):
        super().__init__([child_field_name])
        self.child_field_name = child_field_name

    def download(self, instance, path, asset_names, **kwargs):
        for child_id in getattr(instance, self.child_field_name):
            child_instance = instance.underlying_type.from_id(child_id)
            child_instance.download_assets(path, asset_names, **kwargs)


