import os
import glob
import json
import mimetypes
import re
import subprocess
import shutil

from FLIR.conservator_cli.lib import graphql_api as fca

IMAGE_FILE_SUFFIXES = [
"bmp", "gif", "jpeg", "jpg", "tif", "tiff",
"BMP", "GIF", "JPEG", "JPG", "TIF", "TIFF"
]

VIDEO_FILE_SUFFIXES = [
"mp4", "mpeg", "zip",
"MP4", "MPEG", "ZIP"
]

DEFAULT_MEDIA_SUFFIXES = IMAGE_FILE_SUFFIXES + VIDEO_FILE_SUFFIXES

class Collection:
    # call classmethod instead to have it return None on error.
    def __init__(self, parent_folder, name, collection_id=None, credentials=None, create_nonexistent=False):
        self.id = collection_id
        self.credentials = credentials
        self.parent_folder = os.path.abspath(parent_folder)
        self.root_folder = os.path.join(self.parent_folder, name)
        self.create_nonexistent = create_nonexistent

    @classmethod
    def create(cls, collection_path, credentials, parent_folder=os.getcwd(), create_nonexistent=False):
        data = fca.get_collection_by_path(collection_path, credentials.token)
        if not data:
            if create_nonexistent:
                # try to create missing collections along given conservator path
                self.create_collection_by_path(collection_path)
            else:
                raise LookupError("Collection {} not found!".format(collection_path))

        result = cls(parent_folder, data["name"], data["id"], credentials, create_nonexistent)
        return result

    def conservator_path(self):
        data = fca.get_collection_by_id(self.id, self.credentials.token)
        conservator_path = data["name"]
        while data["parentId"]:
            data = fca.get_collection_by_id(data["parentId"], self.credentials.token)
            conservator_path = data["name"] + "/" + conservator_path
        conservator_path = "/" + conservator_path
        return conservator_path

    def create_collection_by_path(self, collection_path):
        components = collection_path.split("/")
        parent_id = None
        folder_path = ""
        for folder_name in components[1:]:
            folder_path += "/" + folder_name
            data = fca.get_collection_by_path(folder_path, self.credentials.token)
            if not data:
                data = fca.create_collection(folder_name, parent_id, self.credentials.token)

            # this folder will be parent of next one
            parent_id = data["id"]

    def _pull_dataset(self, id, name, parent_folder):
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

    def _download_collections_recursive(self, parent_folder, collection_id, delete=False, include_datasets=False, include_video_metadata=False, include_associated_files=False, include_media=False):
        data = fca.get_collection_by_id(collection_id, self.credentials.token)
        collection_path = os.path.join(parent_folder, data["name"])
        os.makedirs(collection_path, exist_ok=True)
        self._download_video_metadata(data["id"], collection_path, not include_video_metadata, delete)
        self._download_associated_files(data["fileLockerFiles"], collection_path, not include_associated_files, delete)
        self._download_media(collection_id, collection_path, not include_media, delete)
        folder_names = ["associated_files", "video_metadata"]
        folder_names += self._download_datasets(data["id"], collection_path, not include_datasets)
        for id in data["childIds"]:
            name = self._download_collections_recursive(collection_path, id, delete, include_datasets, include_video_metadata, include_associated_files, include_media)
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

    def download_collections_recursively(self, include_datasets=False, include_video_metadata=False, include_associated_files=False, include_media=False, delete=False):
        assert self.credentials is not None, "self.credentials must be set"
        self._download_collections_recursive(self.parent_folder, self.id, delete, include_datasets, include_video_metadata, include_associated_files, include_media)

    def _download_associated_files(self, file_locker, parent_folder, dry_run=True, delete=False):
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

    def _upload_collections_recursive(self, parent_folder, conservator_path, include_datasets=False, include_video_metadata=False, include_associated_files=False, include_media=False):
        #dry_run = True
        dry_run = False # can switch to True for debugging

        # look for files of interest inside local folder 

        # metadata files are in local subfolder called "video_metadata"
        metadata_regex = re.compile(r"/video_metadata$")
        # associated files are in local subfolder called "associated_files"
        associated_regex = re.compile(r"/associated_files$")
        # media files have one of the known filename suffixes
        suffixes = ["\.{}$".format(suffix) for suffix in DEFAULT_MEDIA_SUFFIXES]
        media_regex = re.compile("|".join(suffixes))
        dataset_dirs = []
        metadata_files = []
        associated_files = []
        media_files = []
        for root, dirs, files in os.walk(parent_folder):
            # don't collect files inside datasets, 
            # they should be handled separately
            if "index.json" in files:
                dataset_dirs.append(root)
                dirs[:] = [] # this prevents os.walk() descending into subdirs
                continue

            for filename in files:
                # metadata and associated file patterns are on parent of file, 
                # media file pattern is on filename itself
                if metadata_regex.search(root):
                    metadata_files.append(os.path.join(root, filename))
                elif associated_regex.search(root):
                    associated_files.append(os.path.join(root, filename))
                elif media_regex.search(filename):
                    media_files.append(os.path.join(root, filename))
        #print("DATASETS:", dataset_dirs)
        #print("METADATA:", metadata_files)
        #print("ASSOCIATED:", associated_files)
        #print("MEDIA:", media_files)

        if include_datasets:
            print("WARNING: upload of datasets NYI")
          
        if include_video_metadata:
            metadata_list = []
            metadata = {}
            media_info = {}
            for local_path in metadata_files:
                metadata["local_path"] = local_path
                # find conservator video/image this metadata corresponds to
                with open(local_path) as fp:
                    try:
                       contents = json.load(fp)
                       media_id = contents["videos"][0]["id"]
                    except:
                       print("ERROR: could not find media id in metadata '{}'".format(local_path))
                if media_id:
                    media_info = fca.get_media_from_id(media_id, self.credentials.token)

                if media_info:
                    # found it in conservator
                    metadata["media_id"] = media_info["id"]
                    metadata["media_name"] = media_info["name"]
                    metadata_list.append(dict(metadata))
                else:
                    print("WARNING: no Conservator media corresponding to metadata '{}', skipping".format(local_path))
            self._upload_video_metadata(metadata_list, dry_run)

        if include_associated_files:
            associated_list = []
            associated = {}
            collection_info = {}
            for local_path in associated_files:
                associated["local_path"] = local_path

                # folder path inside conservator matches relative path
                # inside local base directory, except skip "associated_files" 
                # and always use forward slashes
                relative_path = os.path.relpath(local_path, start=parent_folder)
                path_components = relative_path.split(os.sep)
                relative_path = "/".join(path_components[:-2])
                if relative_path:
                    collection_path = conservator_path + "/" + relative_path
                else:
                    collection_path = conservator_path

                collection_info = fca.get_collection_by_path(collection_path, self.credentials.token)
                if not collection_info and self.create_nonexistent:
                    # try to create missing collections along given conservator path
                    self.create_collection_by_path(collection_path)
                    collection_info = fca.get_collection_by_path(collection_path, self.credentials.token)

                if collection_info:
                    # found it in conservator
                    associated["collection_path"] = collection_path
                    associated["collection_id"] = collection_info["id"]
                    associated_list.append(dict(associated))
                else:
                    print("WARNING: Conservator path '{}' not found, skipping {}".format(collection_path, local_path))

            self._upload_associated_files(associated_list, dry_run)

        if include_media:
            media_list = []
            media = {}
            collection_info = {}
            for local_path in media_files:
                media["local_path"] = local_path

                # folder path inside conservator matches relative path
                # inside local base directory, except always use forward slashes
                relative_path = os.path.relpath(local_path, start=parent_folder)
                path_components = relative_path.split(os.sep)
                relative_path = "/".join(path_components[:-1])
                if relative_path:
                    collection_path = conservator_path + "/" + relative_path
                else:
                    collection_path = conservator_path

                collection_info = fca.get_collection_by_path(collection_path, self.credentials.token)
                if not collection_info and self.create_nonexistent:
                    # try to create missing collections along given conservator path
                    self.create_collection_by_path(collection_path)
                    collection_info = fca.get_collection_by_path(collection_path, self.credentials.token)

                if collection_info:
                    # found it in conservator
                    media["collection_path"] = collection_path
                    media["collection_id"] = collection_info["id"]
                    media_list.append(dict(media))
                else:
                    print("WARNING: Conservator path '{}' not found, skipping {}".format(collection_path, local_path))

            self._upload_media(media_list, dry_run)

    def upload_collections_recursively(self, include_datasets=False, include_video_metadata=False, include_associated_files=False, include_media=False):
        assert self.credentials is not None, "self.credentials must be set"
        self._upload_collections_recursive(self.parent_folder, self.conservator_path(), include_datasets, include_video_metadata, include_associated_files, include_media)

    def _detect_content_type(self, local_path):
        (content_type, encoding) = mimetypes.guess_type(local_path)
        if not content_type:
            # assume text files are in utf-8 encoding,
            # anything else will be called binary
            with open(local_path, encoding="utf-8") as fp:
                try:
                    fp.read(1024)
                    content_type = "text/plain"
                except:
                    content_type = "application/octet-stream"

        return content_type

    def _upload_associated_files(self, associated_list, dry_run=True):
        for associated in associated_list:
            local_path = associated["local_path"]
            collection_id = associated["collection_id"]
            collection_path = associated["collection_path"]
            filename = os.path.basename(local_path)
            content_type = self._detect_content_type(local_path)
            print("Upload associated file {} as {} into folder {}".format(filename, content_type, 
                                                                          collection_path))
            if not dry_run:
                url_info = fca.get_signed_collection_locker_url(collection_id, content_type, filename, 
                                                                self.credentials.token)
                fca.upload_video_to_s3(local_path, url_info["signedUrl"], content_type)

    def _upload_datasets(self, datasets, collection_id, dry_run=True):
        # descend into dataset directories and push any changes that have been committed?
        print("WARNING: upload of datasets NYI")

    def _upload_video_metadata(self, metadata_list, dry_run=True):
        content_type = "application/json" # metadata files are always supposed to be json
        for metadata in metadata_list:
            local_path = metadata["local_path"]
            filename = os.path.basename(local_path)
            media_name = metadata["media_name"]
            media_id = metadata["media_id"]
            print("Upload metadata file '{}' as {} for media {} ({})".format(local_path, content_type, 
                                                                             media_name, media_id))
            if not dry_run:
                url_info = fca.get_signed_meta_upload_url(media_id, content_type, filename,
                                                          self.credentials.token)
                fca.upload_video_to_s3(metadata["local_path"], url_info["signedUrl"], content_type)
                fca.mark_annotation_as_uploaded(media_id, url_info["signedUrl"], self.credentials.token)

    def _upload_media(self, media_list, dry_run=True):
        for media in media_list:
            local_path = media["local_path"]
            collection_id = media["collection_id"]
            collection_path = media["collection_path"]
            filename = os.path.basename(local_path)
            content_type = self._detect_content_type(local_path)
            print("Upload media file {} as {} into folder {}".format(filename, content_type, collection_path))

            # don't create multiple copies of same filename in same folder...
            # could implement moving aside old copy, for now keep things simple and just punt
            media_exists = fca.get_media_from_filename(filename, collection_id, self.credentials.token)
            if media_exists:
                print("WARNING: file {} already exists in folder {}, skipping".format(filename, collection_path))
                continue

            if not dry_run:
                create_info = fca.create_video(filename, collection_id, self.credentials.token)
                media_id = create_info["id"]
                url_info = fca.get_signed_upload_url(media_id, content_type, self.credentials.token)
                fca.upload_video_to_s3(local_path, url_info["signedUrl"], content_type)
                # not loading metadata at this time, and not asking for notification when done
                fca.trigger_video_processing(media_id, '', False, self.credentials.token)

    def find_performance_folders(self, rename_map={}):
        folder_paths = {}
        for root, dirs, files in os.walk(self.root_folder):
            basename = os.path.basename(root)
            if "nntc-config" in basename:
                performance_name = os.path.relpath(root, self.root_folder).replace("nntc-config-", "")
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
