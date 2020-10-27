import os

from conservator.types.downloadable import DownloadableType
from conservator.generated import schema
from conservator.types.searchable import SearchableType


class ConservatorMalformedQueryException(Exception):
    pass


class Project(SearchableType):
    underlying_type = schema.Project
    search_query = schema.Query.projects
    by_id_query = schema.Query.project
    problematic_fields = []

    @classmethod
    def query(cls, conservator, **kwargs):
        search_text = kwargs.get("search_text", "")
        # TODO: find out what other characters break projects queries
        bad_chars = ":?\\"
        for char in bad_chars:
            if char in search_text:
                raise ConservatorMalformedQueryException(f"You can't include '{char}' in a projects search string")
        return super(Project, cls).query(conservator, **kwargs)


class Dataset(SearchableType):
    underlying_type = schema.Dataset
    search_query = schema.Query.datasets
    by_id_query = schema.Query.dataset
    problematic_fields = ["shared_with"]


class Video(SearchableType, DownloadableType):
    underlying_type = schema.Video
    search_query = schema.Query.videos
    by_id_query = schema.Query.video
    problematic_fields = ["shared_with"]

    def download(self, path, include_frames=True, include_metadata=False):
        fields = ["name", "url"]
        if include_metadata:
            fields.append("metadata")
        if include_frames:
            fields.append("frames")

        self.populate(fields)
        path = os.path.join(path, self.name)
        print(path)


class Collection(SearchableType, DownloadableType):
    underlying_type = schema.Collection
    search_query = schema.Query.collections
    by_id_query = schema.Query.collection
    problematic_fields = []

    def download(self, path,
                 include_media=False,
                 include_associated_files=False,
                 include_videos=False,
                 include_images=False,
                 include_video_metadata=False,
                 recursive=False):
        """
        Download a Collection to the specified ``path``.

        :param path: The directory to download this collection into. Files will be saved
            at ``os.path.join(path, Collection.name)``.
        :param recursive: If ``True``, recursively download this collection's children
            as subdirectories.
        :param include_media: If ``True``, equivalent to passing ``include_videos=True`` and ``include_images=True``.
        :param include_videos: If ``True``, download videos.
        :param include_images: If ``True``, download images.
        :param include_associated_files: If ``True``, download file locker files, such as the word cloud.
        :param include_video_metadata: "If ``True``, download a JSON file containing metadata for each video
        """
        self.populate(("name", "children", "video_ids", "file_locker_files"))

        path = os.path.join(path, self.name)
        if not os.path.exists(path):
            os.mkdir(path)
        print(f"Downloading into {path}")

        if include_media or include_videos:
            self.download_videos(path, include_metadata=include_video_metadata)

        if include_media or include_images:
            self.download_images(path)

        if include_associated_files:
            self.download_associated_files(path)

        if recursive:
            for child in self.children:
                child.download(path, include_media, include_associated_files, recursive=recursive)

    def download_videos(self, path, include_metadata):
        for video_id in self.video_ids:
            self.populate("videos")
            video = Video.from_id(self._conservator, video_id)
            video.download(path, include_metadata=include_metadata)

    def download_images(self, path):
        for image in self.image_ids:
            pass

    def download_associated_files(self, path):
        for file in self.file_locker_files:
            pass

