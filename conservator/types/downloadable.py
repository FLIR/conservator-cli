from conservator.types.type_proxy import TypeProxy


class DownloadableType(TypeProxy):
    downloadable_assets = None

    def download(self, path, **kwargs):
        raise NotImplementedError

