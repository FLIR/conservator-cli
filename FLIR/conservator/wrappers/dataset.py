import json
import os
import subprocess

from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Mutation,
    Query,
    AddFramesToDatasetInput,
    CreateDatasetInput,
    DeleteDatasetInput,
)
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.wrappers.dataset_frame import DatasetFrame
from FLIR.conservator.wrappers.type_proxy import requires_fields
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.util import download_files


class Dataset(QueryableType):
    underlying_type = schema.Dataset
    by_id_query = schema.Query.dataset
    search_query = schema.Query.datasets

    @classmethod
    def create(cls, conservator, name, collections=None, fields=None):
        """
        Create a dataset with the given `name`, including the given `collections`, if specified.
        The dataset is returned with the requested `fields`.
        """
        if collections is None:
            collections = []
        collection_ids = [collection.id for collection in collections]
        input_ = CreateDatasetInput(name=name, collection_ids=collection_ids)
        dataset = conservator.query(
            Mutation.create_dataset,
            operation_base=Mutation,
            input=input_,
            fields=fields,
        )
        return cls(conservator, dataset)

    def delete(self):
        """
        Delete the dataset.
        """
        input_ = DeleteDatasetInput(id=self.id)
        self._conservator.query(
            Mutation.delete_dataset, operation_base=Mutation, input=input_
        )

    def generate_metadata(self):
        """
        Queries Conservator to generate metadata for the dataset.
        """
        return self._conservator.query(
            Mutation.generate_dataset_metadata,
            operation_base=Mutation,
            dataset_id=self.id,
        )

    def get_frames(self, search_text="", fields=None):
        """
        Returns a paginated query for dataset frames within this dataset, filtering
        with `search_text`.
        """
        return PaginatedQuery(
            self._conservator,
            query=Query.dataset_frames_only,
            wrapping_type=DatasetFrame,
            unpack_field="dataset_frames",
            fields=fields,
            id="RkAXSN4ychHgiNkMk",
            search_text=search_text,
        )

    def add_frames(self, frames, fields=None):
        """
        Given a list of `frames`, add them to the dataset.
        """
        frame_ids = [frame.id for frame in frames]
        _input = AddFramesToDatasetInput(dataset_id=self.id, frame_ids=frame_ids)
        return self._conservator.query(
            Mutation.add_frames_to_dataset,
            operation_base=Mutation,
            fields=fields,
            input=_input,
        )

    def generate_signed_metadata_upload_url(self, filename, content_type):
        """
        Returns a signed url for uploading metadata with the given `filename` and
        `content_type`.
        """
        result = self._conservator.query(
            Mutation.generate_signed_dataset_metadata_upload_url,
            operation_base=Mutation,
            dataset_id=self.id,
            content_type=content_type,
            filename=filename,
        )
        return result.signed_url

    def generate_signed_locker_upload_url(self, filename, content_type):
        """
        Returns a signed url for uploading a new file locker file with the given `filename` and
        `content_type`.
        """
        result = self._conservator.query(
            Mutation.generate_signed_dataset_file_locker_upload_url,
            operation_base=Mutation,
            dataset_id=self.id,
            content_type=content_type,
            filename=filename,
        )
        return result.signed_url

    def get_git_url(self):
        """Returns the Git URL used for cloning this Dataset."""
        return f"{self._conservator.get_authenticated_url()}/git/dataset_{self.id}"

    def get_dvc_url(self):
        """Returns the DVC URL used for downloading files."""
        return f"{self._conservator.get_authenticated_url()}/dvc"

    @requires_fields("name", "repository.master")
    def clone(self, path="."):
        """Clone this Dataset into a subdirectory of `path` based on
        the Dataset's name.

        For instance, if you pass ``path="~/Desktop"``, and want to download a Dataset
        called ``MyFirstDataset``, it will be cloned into ``~/Desktop/MyFirstDataset``.
        """
        path = os.path.join(path, self.name)
        if os.path.exists(path):
            raise FileExistsError(f"Cannot clone to '{path}', already exists.")

        url = self.get_git_url()
        subprocess.call(["git", "clone", url, path])

    @classmethod
    def from_local_path(cls, conservator, path="."):
        """Returns a new Dataset instance using the ID found in ``index.json``
        at the provided `path`
        """
        index_file = os.path.join(path, "index.json")
        if not os.path.exists(index_file):
            raise FileNotFoundError("Missing index.json, check the path")

        with open(index_file) as f:
            data = json.load(f)
            return cls.from_id(conservator, data["datasetId"])

    def pull(
        self,
        path=".",
        include_analytics=False,
        include_eight_bit=True,
        process_count=None,
    ):
        """
        Downloads the files listed in ``index.json`` at the provided `path`.

        :param path: The local path to save files. Should contain an ``index.json`` file.
        :param include_analytics: If `True`, download analytic data to ``analyticsData/``.
        :param include_eight_bit: If `True`, download eight-bit images to ``data/``.
        """
        index_file = os.path.join(path, "index.json")
        if not os.path.exists(index_file):
            raise FileNotFoundError("Missing index.json, check the path")

        data_dir = os.path.join(path, "data")
        if include_eight_bit:
            os.makedirs(data_dir, exist_ok=True)

        analytics_dir = os.path.join(path, "analyticsData")
        if include_analytics:
            os.makedirs(analytics_dir, exist_ok=True)

        assets = []  # (path, name, url)
        base_url = self.get_dvc_url()
        with open(index_file) as f:
            data = json.load(f)
            for frame in data.get("frames", []):
                video_metadata = frame.get("videoMetadata", {})
                video_id = video_metadata.get("videoId", "")
                frame_index = video_metadata["frameIndex"]
                dataset_frame_id = frame["datasetFrameId"]
                if include_eight_bit:
                    md5 = frame["md5"]
                    url = f"{base_url}/{md5[:2]}/{md5[2:]}"
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.jpg"
                    assets.append((data_dir, name, url))

                if include_analytics and ("analyticsMd5" in frame):
                    md5 = frame["analyticsMd5"]
                    url = f"{base_url}/{md5[:2]}/{md5[2:]}"
                    name = f"video-{video_id}-frame-{frame_index:06d}-{dataset_frame_id}.tiff"
                    assets.append((analytics_dir, name, url))

        results = download_files(assets, process_count)

        # See if we have any errors
        total = len(results)
        success = sum(results)
        print(f"Number of Files: {success}, Errors: {total - success}")
