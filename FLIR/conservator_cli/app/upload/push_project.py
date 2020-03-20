#!/usr/bin/env python3
import json
import os
import subprocess

import click

from FLIR.conservator_cli.lib import graphql_api as fca

def upload_collection(folder_root, conservator_path, api_key, include_associated_files=False):
    folder_paths = []
    parent_ids = {}
    for root, dirs, files in os.walk(folder_root):
        path = root.split(os.sep)
        basename = os.path.basename(root)
        if "index.json" in files:
            dirs.clear()
            continue
        collection = fca.get_collection_by_path(os.path.join(conservator_root, root), api_key)
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
                print(upload_results)
        print(root)
        print(collection)
    return folder_paths

@click.command()
@click.argument('folder_root')
@click.option('-p', '--conservator_path', prompt="Path of folder on Conservator", help="Conservator path", default="/")
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
@click.option('-k', '--api_key', prompt="Conservator Api Key", help="Conservator API Key")
def upload_collection_main(folder_root, conservator_root, api_key, include_associated_files):
    """This script recursively uploads FOLDER_ROOT to conservator at parent CONSERVATOR_PATH."""
    upload_collection(folder_root, conservator_path, api_key, include_associated_files)

if __name__ == "__main__":
    upload_collection_main()
