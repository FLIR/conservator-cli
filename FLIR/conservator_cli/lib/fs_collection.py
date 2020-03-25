import os
import json
import subprocess
import shutil

from FLIR.conservator_cli.lib import graphql_api as fca

class Project:
    #call classmethod instead to have it return None on error.
    def __init__(self, collection_id, credentials, parent_folder=None):
        self.id = collection_id
        self.credentials = credentials
        self.parent_folder = os.path.abspath(parent_folder)

    @classmethod
    def create(cls, collection_path, credentials, parent_folder=os.getcwd()):
        data = fca.get_collection_by_path(collection_path, credentials.token)
        if not data:
            raise LookupError("Collection {} not found!".format(collection_path))
        result = cls(data["id"], credentials, parent_folder=parent_folder)
        return result

    def pull_dataset(self, id, name, parent_folder):
        email = self.credentials.email.replace("@", "%40")
        save = os.getcwd()
        os.chdir(parent_folder)
        if os.path.exists(name):
            os.chdir(name)
            subp = subprocess.call(["git", "pull"])
            subp = subprocess.call(["./cvc.py", "pull"])
            subp = subprocess.call(["./cvc.py", "pull"])
        else:
            subp = subprocess.call(["git", "clone", "https://{}@flirconservator.com/git/dataset_{}".format(email, id), "{}".format(name)])
            os.chdir(name)
            subp = subprocess.call(["./cvc.py", "remote", "add", "https://{}:{}@flirconservator.com/dvc".format(email, self.credentials.token)])
            subp = subprocess.call(["./cvc.py", "pull"])
            subp = subprocess.call(["./cvc.py", "pull"])
        os.chdir(save)

    def _download_collections_recursive(self, parent_folder, collection_id, delete=False, include_datasets=False, include_video_metadata=False, include_associated_files=False):
        data = fca.get_collection_by_id(collection_id, self.credentials.token)
        collection_path = os.path.join(parent_folder, data["name"])
        os.makedirs(collection_path, exist_ok=True)
        self.download_video_metadata(data["id"], collection_path, not include_video_metadata, delete)
        self.download_associated_files(data["fileLockerFiles"], collection_path, not include_associated_files, delete)
        folder_names = ["associated_files", "video_metadata"]
        folder_names += self.download_datasets(data["id"], collection_path, not include_datasets)
        for id in data["childIds"]:
            name = self._download_collections_recursive(collection_path, id, delete, include_datasets, include_video_metadata, include_associated_files)
            folder_names.append(name)
        if delete:
            for node in os.listdir(collection_path):
                if node in folder_names:
                    continue
                try:
                    shutil.rmtree(os.path.join(collection_path, node))
                except:
                    os.remove(os.path.join(collection_path, node))
        return data["name"]

    def download_collections_recursively(self, include_datasets=False, include_video_metadata=False, include_associated_files=False, delete=False):
        self._download_collections_recursive(self.parent_folder, self.id, delete, include_datasets, include_video_metadata, include_associated_files)

    def download_associated_files(self, file_locker, parent_folder, dry_run=True, delete=False):
        os.makedirs(os.path.join(parent_folder, "associated_files"), exist_ok=True)
        if not dry_run:
            for file in file_locker:
                fca.download_file(os.path.join(parent_folder, "associated_files", file["name"]), file["url"], self.credentials.token)
        associated_filenames=[associated_file["name"] for associated_file in file_locker]
        if delete:
            for root, dirs, files in os.walk(os.path.join(parent_folder, "associated_files")):
                for file in files:
                    if not file in associated_filenames:
                        try:
                            shutil.rmtree(os.path.join(root, file))
                        except:
                            os.remove(os.path.join(root, file))
                break
        return associated_filenames

    def download_datasets(self, collection_id, parent_folder, dry_run=True):
        datasets = fca.get_datasets_from_collection(collection_id, self.credentials.token)
        if not dry_run:
            for dataset in datasets:
                self.pull_dataset(dataset["id"], dataset["name"], parent_folder)
        return [dataset["name"] for dataset in datasets]

    def download_video_metadata(self, collection_id, parent_folder, dry_run=True, delete=False):
        os.makedirs(os.path.join(parent_folder, "video_metadata"), exist_ok=True)
        videos = fca.get_videos_from_collection(collection_id, self.credentials.token)
        video_names = []
        for video in videos:
            metadata = fca.get_video_metadata(video["id"], self.credentials.token)["metadata"]
            obj = json.loads(metadata)
            obj["videos"][0]["name"] = video["name"]
            filename = ".".join(video["name"].split(".")[:-1] + ["json"])
            video_names.append(filename)
            if not dry_run:
                with open(os.path.join(parent_folder, "video_metadata", filename), "w") as file:
                    json.dump(obj, file, indent=4, separators=(',', ': '))
        if delete:
            for root, dirs, files in os.walk(os.path.join(parent_folder, "video_metadata")):
                for file in files:
                    if not file in video_names:
                        try:
                            shutil.rmtree(os.path.join(root, file))
                        except:
                            os.remove(os.path.join(root, file))
                break
        return video_names
