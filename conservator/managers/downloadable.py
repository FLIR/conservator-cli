from conservator.managers.type_manager import TypeManager
from conservator.types import DownloadableType


class DownloadableTypeManager(TypeManager):
    def __init__(self, conservator, downloadable_type):
        assert issubclass(downloadable_type, DownloadableType)
        super().__init__(conservator, downloadable_type)

    def download_from_id(self, idx, path, **kwargs):
        instance = self.underlying_type.from_id(self.conservator, idx)
        instance.download_assets(path, **kwargs)
