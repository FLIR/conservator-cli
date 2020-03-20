import os
import json
import subprocess

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

    def _download_collections_recursive(self, parent_folder, collection_id, node_function, delete=False):
        data = fca.get_collection_by_id(collection_id, self.credentials.token)
        collection_path = os.path.join(parent_folder, data["name"])
        os.makedirs(collection_path, exist_ok=True)
        child_names = node_function(self.credentials, data, collection_path)
        for id in data["childIds"]:
            name = self._download_collections_recursive(collection_path, id, node_function, delete)
            child_names.append(name)
        if delete:
            for node in os.listdir(collection_path):
                if node in child_names:
                    continue
                try:
                    shutil.rmtree(os.path.join(collection_path, node))
                except:
                    os.remove(os.path.join(collection_path, node))
        return data["name"]

    def download_collections_recursively(self, include_datasets=False, include_video_metadata=False, include_associated_files=False, delete=False):
        def node_function(credentials, collection_data, collection_path):
            child_names = []
            child_names += self.download_datasets(collection_data["id"], collection_path, not include_datasets)
            child_names += self.download_video_metadata(collection_data["id"], collection_path, not include_video_metadata)
            child_names += self.download_associated_files(collection_data["fileLockerFiles"], collection_path, not include_associated_files)
            return child_names
        self._download_collections_recursive(self.parent_folder, self.id, node_function, delete)

    def download_associated_files(self, file_locker, parent_folder, dry_run=True):
        if not dry_run:
            for file in file_locker:
                fca.download_file(os.path.join(parent_folder, file["name"]), file["url"], self.credentials.token)
        return [associated_file["name"] for associated_file in file_locker]

    def download_datasets(self, collection_id, parent_folder, dry_run=True):
        datasets = fca.get_datasets_from_collection(collection_id, self.credentials.token)
        if not dry_run:
            for dataset in datasets:
                self.pull_dataset(dataset["id"], dataset["name"], parent_folder)
        return [dataset["name"] for dataset in datasets]

    def download_video_metadata(self, collection_id, parent_folder, dry_run=True):
        videos = fca.get_videos_from_collection(collection_id, self.credentials.token)
        video_names = []
        for video in videos:
            metadata = fca.get_video_metadata(video["id"], self.credentials.token)["metadata"]
            obj = json.loads(metadata)
            obj["videos"][0]["name"] = video["name"]
            filename = ".".join(video["name"].split(".")[:-1] + ["json"])
            video_names.append(filename)
            if not dry_run:
                with open(os.path.join(parent_folder, filename), "w") as file:
                    json.dump(obj, file, indent=4, separators=(',', ': '))
        return video_names
