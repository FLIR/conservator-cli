import json
import os
import shutil
import subprocess

from FLIR.conservator_cli.lib import graphql_api as fca


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

    def _pull_dataset(self, id, name, parent_folder):
        save = os.getcwd()
        os.chdir(parent_folder)
        if os.path.exists(name):
            os.chdir(name)
            subp = subprocess.call(["git", "pull"])
            subp = subprocess.call(["python", "./cvc.py", "pull"])
            subp = subprocess.call(["python", "./cvc.py", "pull"])
        else:
            subp = subprocess.call(["git", "clone",
                                    "https://{}@flirconservator.com/git/dataset_{}".format(
                                        self.credentials.get_url_format(), id),
                                    "{}".format(name)])
            os.chdir(name)
            subp = subprocess.call(["python", "./cvc.py", "remote", "add",
                                    "https://{}@flirconservator.com/dvc".format(self.credentials.get_url_format())])
            subp = subprocess.call(["python", "./cvc.py", "pull"])
            subp = subprocess.call(["python", "./cvc.py", "pull"])
        os.chdir(save)

    def _download_collections_recursive(self, parent_folder, collection_id, delete=False, include_datasets=False,
                                        include_video_metadata=False, include_associated_files=False,
                                        include_media=False):
        data = fca.get_collection_by_id(collection_id, self.credentials.token)
        collection_path = os.path.join(parent_folder, data["name"])
        os.makedirs(collection_path, exist_ok=True)
        self._download_video_metadata(data["id"], collection_path, not include_video_metadata, delete)
        self._download_associated_files(data["fileLockerFiles"], collection_path, not include_associated_files, delete)
        self._download_media(collection_id, collection_path, not include_media, delete)
        folder_names = ["associated_files", "video_metadata"]
        folder_names += self._download_datasets(data["id"], collection_path, not include_datasets)
        for id in data["childIds"]:
            name = self._download_collections_recursive(collection_path, id, delete, include_datasets,
                                                        include_video_metadata, include_associated_files, include_media)
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

    def download_collections_recursively(self, include_datasets=False, include_video_metadata=False,
                                         include_associated_files=False, include_media=False, delete=False):
        assert self.credentials is not None, "self.credentials must be set"
        self._download_collections_recursive(self.parent_folder, self.id, delete, include_datasets,
                                             include_video_metadata, include_associated_files, include_media)

    def _download_associated_files(self, file_locker, parent_folder, dry_run=True, delete=False):
        os.makedirs(os.path.join(parent_folder, "associated_files"), exist_ok=True)
        if not dry_run:
            for file in file_locker:
                fca.download_file(os.path.join(parent_folder, "associated_files", file["name"]), file["url"],
                                  self.credentials.token)
        associated_filenames = [associated_file["name"] for associated_file in file_locker]
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

    def _download_datasets(self, collection_id, parent_folder, dry_run=True):
        datasets = fca.get_datasets_from_collection(collection_id, self.credentials.token)
        if not dry_run:
            for dataset in datasets:
                self._pull_dataset(dataset["id"], dataset["name"], parent_folder)
        return [dataset["name"] for dataset in datasets]

    def _download_video_metadata(self, collection_id, parent_folder, dry_run=True, delete=False):
        os.makedirs(os.path.join(parent_folder, "video_metadata"), exist_ok=True)
        videos = fca.get_videos_from_collection(collection_id, self.credentials.token)
        video_names = []
        for video in videos:
            metadata = fca.get_video_metadata(video["id"], self.credentials.token)["metadata"]
            obj = json.loads(metadata)
            obj["videos"][0]["name"] = video["name"]
            filename = ".".join(video["filename"].split(".")[:-1] + ["json"])
            video_names.append(filename)
            if not dry_run:
                with open(os.path.join(parent_folder, "video_metadata", filename), "w") as file:
                    json.dump(obj, file, indent=4, separators=(',', ': '))
        if delete:
            for root, dirs, files in os.walk(os.path.join(parent_folder, "video_metadata")):
                for file in files:
                    if file not in video_names:
                        try:
                            shutil.rmtree(os.path.join(root, file))
                        except:
                            os.remove(os.path.join(root, file))
                break
        return video_names

    def _download_media(self, collection_id, parent_folder, dry_run=True, delete=False):
        if (delete):
            print("Warning: delete NYI for downloading media")

        videos = fca.get_video_filelist(collection_id, self.credentials.token)
        if not dry_run:
            for video in videos:
                print("{} -> {}".format(video["url"], os.path.join(parent_folder, video["filename"])))
                fca.download_file(os.path.join(parent_folder, video["filename"]), video["url"], self.credentials.token)

        images = fca.get_image_filelist(collection_id, self.credentials.token)
        if not dry_run:
            for image in images:
                print("{} -> {}".format(image["url"], os.path.join(parent_folder, image["filename"])))
                fca.download_file(os.path.join(parent_folder, image["filename"]), image["url"], self.credentials.token)

    def find_performance_folders(self, rename_map={}):
        folder_paths = {}
        for root, dirs, files in os.walk(self.root_folder):
            basename = os.path.basename(root)
            if "nntc-config" in basename:
                performance_name = os.path.relpath(root, self.root_folder).replace('nntc-config-', '')
                folder_paths[performance_name] = root
        return folder_paths

    def find_dataset_folders(self, rename_map={}):
        folder_paths = {}
        for root, dirs, files in os.walk(self.root_folder):
            dataset_name = os.path.basename(root)
            if "index.json" in files:
                dataset_name = rename_map.get(dataset_name, dataset_name)
                folder_paths[dataset_name] = root
        return folder_paths
