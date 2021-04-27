import json
import os

from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import (
    Mutation,
    Query,
    AddFramesToDatasetInput,
    CreateDatasetInput,
    DeleteDatasetInput,
)
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.wrappers.file_locker import FileLockerType
from FLIR.conservator.wrappers.metadata import MetadataType
from FLIR.conservator.wrappers.queryable import QueryableType
from FLIR.conservator.wrappers.type_proxy import requires_fields


class Dataset(QueryableType, FileLockerType, MetadataType):
    underlying_type = schema.Dataset
    by_id_query = schema.Query.dataset
    search_query = schema.Query.datasets

    # name of id field in mutations when not simply 'id'
    id_type = "dataset_id"

    # file-locker operations
    file_locker_gen_url = Mutation.generate_signed_dataset_file_locker_upload_url
    file_locker_remove = Mutation.remove_dataset_file_locker_file

    # metadata operations
    metadata_gen_url = Mutation.generate_signed_dataset_metadata_upload_url
    metadata_confirm_url = Mutation.mark_dataset_annotation_as_uploaded

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
            Mutation.delete_dataset,
            input=input_,
            fields="id",
        )

    def generate_metadata(self):
        """
        Queries Conservator to generate metadata for the dataset.
        """
        return self._conservator.query(
            Mutation.generate_dataset_metadata,
            dataset_id=self.id,
        )

    @requires_fields("name")
    def download_metadata(self, path):
        """
        Downloads metadata to `path/name.json`,
        where `name` is the dataset's name.
        """
        metadata = self.generate_metadata()
        json_data = json.loads(metadata)
        json_file = f"{self.name}.json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(",", ": "))

    def get_frames(self, search_text="", fields=None):
        """
        Returns a paginated query for dataset frames within this dataset, filtering
        with `search_text`.
        """
        return PaginatedQuery(
            self._conservator,
            query=Query.dataset_frames_only,
            unpack_field="dataset_frames",
            fields=fields,
            id=self.id,
            search_text=search_text,
        )

    def add_frames(self, frames, fields=None, overwrite=False):
        """
        Given a list of `frames`, add them to the dataset.  If overwrite
        is True and the frame was already in the dataset, the dataset frame
        attributes will be replaced with the source frame attributes.
        """
        frame_ids = [frame.id for frame in frames]
        _input = AddFramesToDatasetInput(
            dataset_id=self.id, frame_ids=frame_ids, overwrite=overwrite
        )
        return self._conservator.query(
            Mutation.add_frames_to_dataset,
            fields=fields,
            input=_input,
        )

    def get_git_url(self):
        """Returns the Git URL used for cloning this Dataset."""
        return f"{self._conservator.get_authenticated_url()}/git/dataset_{self.id}"

    def commit(self, message):
        """
        Commits changes to the dataset made outside of CVC/Git system (for instance,
        using the Web UI, or most methods within this class). The current user will
        be the author of the commit.

        :param message: The commit message.
        """
        user = self._conservator.get_user()
        return self._conservator.query(
            Mutation.commit_dataset,
            dataset_id=self.id,
            commit_message=message,
            user_id=user.id,
        )

    @requires_fields("repository.master")
    def get_commit_history(self, fields=None):
        """
        Returns a list of version control commits for the Dataset. Note
        that some older datasets may not have a repository, causing this
        method to fail.
        """
        return self._conservator.query(
            query=Query.commit_history_by_id, fields=fields, id=self.repository.master
        )

    def get_commit_by_id(self, commit_id="HEAD", fields=None):
        """
        Returns a specific commit from a `commit_id`. The ID can be a hash, or an
        identifier like ``HEAD``.
        """
        return self._conservator.query(
            query=Query.git_commit,
            fields=fields,
            dataset_id=self.id,
            commit_id=commit_id,
        )

    def get_root_tree_id(self, commit_id="HEAD"):
        """
        Returns the id (hash) of the tree at the given `commit_id`. The ID
        can be a hash, or an identifier like ``HEAD``.

        Defaults to the latest commit.
        """
        commit = self.get_commit_by_id(commit_id=commit_id, fields="tree")
        return commit.tree

    def get_tree_by_id(self, tree_id="HEAD", fields=None):
        """
        Returns a tree from a `tree_id`. The ID can be a hash, or an
        identifier like ``HEAD``.
        """
        return self._conservator.query(
            query=Query.git_tree, fields=fields, dataset_id=self.id, tree_id=tree_id
        )

    def get_blob_url_by_id(self, blob_id):
        """
        Returns a URL that can be used to download a blob. A `blob_id` can be
        gotten using :meth:`~FLIR.conservator.wrappers.dataset.Dataset.get_tree_by_id`.
        """
        return f"{self.get_git_url()}/get_blob/{blob_id}"

    def get_blob_id_by_name(self, filename, commit_id="HEAD"):
        """
        Returns a blob's id (hash) from `filename`. This searches the root directory of
        the given `commit_id`, and then searches `associated_files`. It returns the hash of
        the first blob found with a matching name.
        """
        fields = ["tree_list.name", "tree_list._id", "tree_list.type"]
        root_tree_id = self.get_root_tree_id(commit_id)
        root_tree = self.get_tree_by_id(tree_id=root_tree_id, fields=fields)
        associated_files_tree_id = None
        for item in root_tree.tree_list:
            if item.name == filename and item.type == "blob":
                return item._id
            if item.name == "associated_files" and item.type == "tree":
                associated_files_tree_id = item._id

        associated_files_tree = self.get_tree_by_id(
            tree_id=associated_files_tree_id, fields=fields
        )
        for item in associated_files_tree.tree_list:
            if item.name == filename and item.type == "blob":
                return item._id

        raise FileNotFoundError(
            f"File '{filename}' not found in the dataset repository at commit '{commit_id}'"
        )

    def download_blob_by_name(self, filename, path, commit_id="HEAD"):
        """
        Download a blob to the specified `path`. A `blob_id` can be
        gotten using :meth:`~FLIR.conservator.wrappers.dataset.Dataset.get_tree_by_id`.

        If `path` is a file, the blob will be saved to that file. If it is a directory,
        the blob will be saved to a file named `filename` within the directory at `path`.
        """
        path = os.path.abspath(path)
        if os.path.isdir(path):
            path = os.path.join(path, filename)

        blob_id = self.get_blob_id_by_name(filename, commit_id=commit_id)
        self.download_blob(blob_id, path)

    def download_blob(self, blob_id, path):
        """
        Download a blob to the specified `path`. A `blob_id` can be
        gotten using :meth:`~FLIR.conservator.wrappers.dataset.Dataset.get_tree_by_id`.
        """
        path = os.path.abspath(path)
        if os.path.exists(path):
            raise FileExistsError("Blob download path must not exist")

        url = self.get_blob_url_by_id(blob_id)
        parent, _ = os.path.split(path)
        os.makedirs(parent, exist_ok=True)
        self._conservator.files.download(url=url, local_path=path)

    def download_latest_index(self, path):
        """
        Downloads the Dataset's latest ``index.json`` file to the
        specified path. If the path is a directory, the file will
        be downloaded to ``index.json`` within that directory.

        This can be used as a faster alternative to a full repository
        clone for some operations.
        """
        self.download_blob_by_name("index.json", path, commit_id="HEAD")

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
