#!/usr/bin/env python3
import argparse
import os

from pyconservator.legacy import graphql_api as fca


def upload_associated_files(associated_file_folder, collection_id, api_key):
    for root, dirs, associated_files in os.walk(os.path.join(associated_file_folder)):
        for filename in associated_files:
            if filename in ["wordcloud.png"]:
                continue
            if filename.endswith(".png"):
                application_type = "image/png"
            elif filename.endswith(".json"):
                application_type = "application/json"
            elif filename.endswith(".csv"):
                application_type = "text/csv"
            else:
                print("WARNING: File type of {} not supported, contributions accepted!".format(filename))
                continue
            data = fca.get_signed_collection_locker_url(collection_id, application_type, filename, api_key)
            upload_results = fca.upload_video_to_s3(os.path.join(root, filename), data["signedUrl"], application_type)
        break


def upload_collection(folder_root, root_collection_path, api_key, include_associated_files=False):
    folder_paths = []
    parent_ids = {}
    if root_collection_path != "/":
        conservator_root = fca.get_collection_by_path(str(root_collection_path), api_key)
        if not conservator_root:
            print("Error: root_collection_path {} does not exist".format(root_collection_path))
            exit()
        parent_ids[os.path.dirname(folder_root)] = conservator_root["id"]
    for root, dirs, files in os.walk(folder_root):
        relpath = os.path.relpath(root, start=os.path.dirname(folder_root))
        parent_path = os.path.dirname(root)
        basename = os.path.basename(root)
        if "index.json" in files:
            dirs.clear()
            continue
        if "video_metadata" in dirs:
            dirs.remove("video_metadata")
        collection_path = os.path.abspath(os.path.join(root_collection_path, relpath))
        collection = fca.get_collection_by_path(str(collection_path), api_key)
        if not collection and not parent_path in parent_ids:
            print("ERROR: Could not find {} at root / in conservator.".format(relpath))
            exit()
        collection = collection or fca.create_collection(basename, parent_ids[parent_path], api_key)
        parent_ids[root] = collection["id"]
        if "associated_files" in dirs and include_associated_files:
            upload_associated_files(os.path.join(root, "associated_files"), collection["id"], api_key)
            dirs.remove("associated_files")
        for file in files:
            print("WARNING: File type of {} not supported, contributions accepted!".format(os.path.join(root, file)))
    return folder_paths


def upload_collection_main():
    """
    This script recursively uploads FOLDER_ROOT to conservator at parent CONSERVATOR_PARENT_PATH. Folder is uploaded with the same name that is on disk.
    See upload_associated_file for a list of supported file extensions.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('folder_root', help="path of folder to upload to conservator as a collection")
    parser.add_argument('-a', '--include_associated_files', help="upload associated files", action='store_true')
    parser.add_argument('-p', '--conservator_parent_path', help="conservator path to the parent collection",
                        default="/")
    parser.add_argument('-k', '--api_key', help="Conservator API Key", required=True)
    args = parser.parse_args()
    upload_collection(os.path.abspath(args.folder_root), os.path.abspath(args.conservator_parent_path), args.api_key,
                      args.include_associated_files)


if __name__ == "__main__":
    upload_collection_main()
