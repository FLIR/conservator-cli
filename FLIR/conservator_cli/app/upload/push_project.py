#!/usr/bin/env python3
import json
import os
import subprocess
import argparse

from FLIR.conservator_cli.lib import graphql_api as fca

def upload_collection(folder_root, conservator_path, api_key, include_associated_files=False):
    folder_paths = []
    parent_ids = {}
    conservator_root = fca.get_collection_by_path(str(collection_path), api_key)
    if not conservator_root:
        print("conservator_path {} does not exist".format(conservator_path))
        exit()
    parent_ids[os.path.dirname(folder_root)] = conservator_root["id"]
    for root, dirs, files in os.walk(folder_root):
        path = root.split(os.sep)
        basename = os.path.basename(root)
        if "index.json" in files:
            dirs.clear()
            continue
        collection_path = os.path.join(conservator_path, root)
        collection = fca.get_collection_by_path(str(collection_path), api_key)
        collection = collection or fca.create_collection(basename, parent_ids[os.path.dirname(root)], api_key)
        parent_ids[root] = collection["id"]
        if include_associated_files:
            for filename in files:
                if filename in ["wordcloud.png"]:
                    continue
                if filename.endswith(".png"):
                    application_type = "image/png"
                elif filename.endswith(".json"):
                    application_type = "application/json"
                elif filename.endswith(".csv"):
                    application_type = "text/csv"
                else:
                    continue
                data = fca.get_signed_collection_locker_url(collection["id"], application_type, filename, api_key)
                upload_results = fca.upload_video_to_s3(os.path.join(root, filename), data["signedUrl"], application_type)
    return folder_paths

def upload_collection_main():
    """This script recursively uploads FOLDER_ROOT to conservator at parent CONSERVATOR_PATH. Folder is uploaded with the same name."""
    parser = argparse.ArgumentParser()
    parser.add_argument('folder_root', help="path of folder to upload to conservator as a collection")
    parser.add_argument('-a', '--include_associated_files', help="download associated files", action='store_true')
    parser.add_argument('-p', '--conservator_path', help="Conservator path", default="/")
    parser.add_argument('-k', '--api_key', help="Conservator API Key", required=True)
    args = parser.parse_args()
    upload_collection(args.folder_root, args.conservator_path, args.api_key, args.include_associated_files)

if __name__ == "__main__":
    upload_collection_main()
