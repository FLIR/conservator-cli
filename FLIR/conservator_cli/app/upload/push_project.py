#!/usr/bin/env python3
import click
import json
import os
import subprocess

from FLIR.conservator_cli.lib import graphql_api as fca


def find_folders(project_root, conservator_token):
    folder_paths = []
    parent_ids = {}
    for root, dirs, files in os.walk(project_root):
        path = root.split(os.sep)
        basename = os.path.basename(root)
        if "index.json" in files:
            dirs.clear()
            continue
        collection = fca.get_collection_by_path("/"+root, conservator_token)

        if not collection:
            collection = fca.create_collection(basename, parent_ids[os.path.dirname(root)], conservator_token)
        parent_ids[root] = collection["id"]
        for file in files:
            if file in ["wordcloud.png"]:
                continue
            if file.endswith(".png"):
                application_type = "image/png"
            elif file.endswith(".json"):
                application_type = "application/json"
            elif file.endswith(".csv"):
                application_type = "text/csv"
            else:
                continue
            data = fca.get_signed_collection_locker_url(collection["id"], application_type, file, conservator_token)
            upload_results = fca.upload_video_to_s3(os.path.join(root, file), data["signedUrl"], application_type)
            print(upload_results)
        print(root)
        print(collection)
    return folder_paths

def find_dataset_folders(project_root, rename_map={}):
    folder_paths = {}
    for root, dirs, files in os.walk(project_root):
        path = root.split(os.sep)
        basename = os.path.basename(root)
        if "index.json" in files:
            print("Found dataset: {}".format(root))
            dataset_name = os.path.basename(root)
            dataset_name = rename_map.get(dataset_name, dataset_name)
            folder_paths[dataset_name] = root
    return folder_paths

@click.command()
@click.argument('collection_path')
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
def download_project_main(collection_path, conservator_token, include_associated_files):
    find_folders(collection_path, conservator_token)


if __name__ == "__main__":
    download_project_main()
