import abc
import functools
import os

from conservator.connection import ConservatorGraphQLServerError, ConservatorMalformedQueryException
from conservator.generated import schema
from conservator.util import to_python_field_name


class TypeProxyMetaclass:
    pass


class TypeProxy(abc.ABC):
    underlying_type = None
    by_id_query = None
    search_query = None
    problematic_fields = None
    always_fields = (
        'id',
    )

    def __init__(self, conservator, instance):
        self._conservator = conservator
        self._instance = instance
        self._initialized_fields = list(filter(lambda f: not f.startswith('_'),
                                               instance.__dict__))

    def __getattr__(self, item):
        value = getattr(self._instance, item)

        if item in self._initialized_fields:
            return value

        raise AttributeError

    @classmethod
    def handle_query_error(cls, e):
        new_problematic_fields = cls.problematic_fields[:]
        for error in e.errors:
            if "Cannot return null for non-nullable field" in error["message"]:
                fields = filter(lambda i: isinstance(i, str), error["path"])
                problematic_field = list(fields)[1]
                name = to_python_field_name(cls.underlying_type, problematic_field)
                if name not in new_problematic_fields:
                    print("Server encountered an error due to a null value for a non-nullable field.")
                    print("Attempting to resolve by excluding field in future queries.")
                    print("Excluded field:", name)
                    new_problematic_fields.append(name)
                if name in cls.problematic_fields:
                    raise Exception(f"Field '{name}' was included despite being problematic.")
                continue

            # can't handle this error
            raise
        cls.problematic_fields = new_problematic_fields

    @classmethod
    def get_all_fields(cls):
        fields = []
        for field in cls.underlying_type:
            fields.append(field.name)
        return fields

    def populate_all(self):
        self.populate(self.get_all_fields())

    def populate(self, fields=()):
        if self.by_id_query is None:
            raise NotImplementedError
        try:
            request_fields = tuple(filter(lambda f: f not in self.problematic_fields, fields))
            result = self._conservator.query(self.by_id_query, id=self.id, fields=request_fields)
            for field in request_fields:
                v = getattr(result, field)
                setattr(self._instance, field, v)
                self._initialized_fields.append(field)
        except ConservatorGraphQLServerError as e:
            # Some errors are recoverable.
            # If it isn't, the handler will re-raise the exception.
            self.handle_query_error(e)
            self.populate(fields)

    @classmethod
    def from_id(cls, conservator, id_):
        base_item = cls.underlying_type({"id": id_})
        return cls(conservator, base_item)
        

class QueryableType(TypeProxy):
    @classmethod
    def query(cls, conservator, **kwargs):
        results = cls.do_query(conservator, **kwargs)
        return list(map(lambda r: cls(conservator, r), results))

    @classmethod
    def do_query(cls, conservator, fields=(), **kwargs):
        try:
            unfiltered_fields = cls.always_fields + tuple(fields)
            requested_fields = tuple(filter(lambda f: f not in cls.problematic_fields, unfiltered_fields))
            results = conservator.query(cls.search_query,
                                        fields=requested_fields,
                                        **kwargs)
            return results
        except ConservatorGraphQLServerError as e:
            # Some errors are recoverable.
            # If it isn't, the handler will re-raise the exception.
            cls.handle_query_error(e)
            return cls.do_query(conservator, fields, **kwargs)


class DownloadableType(abc.ABC):
    @abc.abstractmethod
    def download(self, path, **kwargs):
        raise NotImplementedError


class Project(QueryableType):
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


class Dataset(QueryableType):
    underlying_type = schema.Dataset
    search_query = schema.Query.datasets
    by_id_query = schema.Query.dataset
    problematic_fields = ["shared_with"]


class Video(QueryableType):
    underlying_type = schema.Video
    search_query = schema.Query.videos
    by_id_query = schema.Query.video
    problematic_fields = []


class Collection(QueryableType, DownloadableType):
    underlying_type = schema.Collection
    search_query = schema.Query.collections
    by_id_query = schema.Query.collection
    problematic_fields = []

    def download(self, path,
                 include_media=False,
                 include_associated_files=False,
                 include_videos=False,
                 include_images=False,
                 include_metadata=False,
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
        :param include_metadata: "If ``True``, download a JSON file containing metadata about this Collection.
        """
        self.populate(("name", "children", "video_ids", "file_locker_files"))

        path = os.path.join(path, self.name)
        if not os.path.exists(path):
            os.mkdir(path)
        print(f"Downloading into {path}")

        if include_media or include_videos:
            self.download_videos(path)

        if include_media or include_images:
            self.download_images(path)

        if include_associated_files:
            self.download_associated_files(path)

        if include_metadata:
            self.download_metadata(path)

        if recursive:
            for child in self.children:
                child.download(path, include_media, include_associated_files, recursive=recursive)

    def download_metadata(self, path):
        pass

    def download_videos(self, path):
        for video_id in self.video_ids:
            video = Video.from_id(self._conservator, video_id)
            video.download(path)

    def download_images(self, path):
        for image in self.image_ids:
            pass

    def download_associated_files(self, path):
        for file in self.file_locker_files:
            pass

