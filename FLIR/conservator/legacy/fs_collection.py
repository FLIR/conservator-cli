import json
import os
import shutil


class Collection:
    # call classmethod instead to have it return None on error.
    def __init__(self, parent_folder, name, collection_id=None, credentials=None):
        self.id = collection_id
        self.credentials = credentials
        self.parent_folder = os.path.abspath(parent_folder)
        self.root_folder = os.path.join(self.parent_folder, name)

    @classmethod
    def create(cls, collection_path, credentials, parent_folder=os.getcwd()):
        data = fca.get_collection_by_path(collection_path, credentials.token)
        if not data:
            raise LookupError("Collection {} not found!".format(collection_path))
        result = cls(parent_folder, data["name"], data["id"], credentials)
        return result

    def _download_collections_recursive(self, parent_folder, collection_id, include_datasets=False,
                                        include_video_metadata=False, include_associated_files=False,
                                        include_media=False):
        data = fca.get_collection_by_id(collection_id, self.credentials.token)
        collection_path = os.path.join(parent_folder, data["name"])
        os.makedirs(collection_path, exist_ok=True)
        if include_video_metadata:
            self._download_video_metadata(data["id"], collection_path)
        if include_associated_files:
            self._download_associated_files(data["fileLockerFiles"], collection_path)
        if include_media:
            self._download_media(collection_id, collection_path)
        if include_datasets:
            self._download_datasets(data["id"], collection_path)
        for id_ in data["childIds"]:
            self._download_collections_recursive(collection_path, id_, include_datasets,
                                                 include_video_metadata, include_associated_files, include_media)

    def download_collections_recursively(self, include_datasets=False, include_video_metadata=False,
                                         include_associated_files=False, include_media=False, delete=False):
        assert self.credentials is not None, "self.credentials must be set"
        self._download_collections_recursive(self.parent_folder, self.id, delete, include_datasets,
                                             include_video_metadata, include_associated_files, include_media)

    def _download_associated_files(self, file_locker, parent_folder):
        os.makedirs(os.path.join(parent_folder, "associated_files"), exist_ok=True)
        for file in file_locker:
            fca.download_file(os.path.join(parent_folder, "associated_files", file["name"]), file["url"],
                              self.credentials.token)

    def _download_datasets(self, collection_id, parent_folder):
        datasets = fca.get_datasets_from_collection(collection_id, self.credentials.token)
        for dataset in datasets:
            self._pull_dataset(dataset["id"], dataset["name"], parent_folder)

    def _download_video_metadata(self, collection_id, parent_folder):
        os.makedirs(os.path.join(parent_folder, "video_metadata"), exist_ok=True)
        videos = fca.get_videos_from_collection(collection_id, self.credentials.token)
        for video in videos:
            metadata = fca.get_video_metadata(video["id"], self.credentials.token)["metadata"]
            obj = json.loads(metadata)
            obj["videos"][0]["name"] = video["name"]
            filename = ".".join(video["filename"].split(".")[:-1] + ["json"])
            with open(os.path.join(parent_folder, "video_metadata", filename), "w") as file:
                json.dump(obj, file, indent=4, separators=(',', ': '))

    def _download_media(self, collection_id, parent_folder):
        videos = fca.get_video_filelist(collection_id, self.credentials.token)
        for video in videos:
            print("{} -> {}".format(video["url"], os.path.join(parent_folder, video["filename"])))
            fca.download_file(os.path.join(parent_folder, video["filename"]), video["url"], self.credentials.token)

        images = fca.get_image_filelist(collection_id, self.credentials.token)
        for image in images:
            print("{} -> {}".format(image["url"], os.path.join(parent_folder, image["filename"])))
            fca.download_file(os.path.join(parent_folder, image["filename"]), image["url"], self.credentials.token)
