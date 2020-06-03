#!/usr/bin/env python3
import click
import json
import os
import subprocess

from FLIR.conservator_cli.lib import graphql_api as fca
from FLIR.conservator_cli.lib.fs_collection import Collection
from FLIR.conservator_cli.lib.conservator_credentials import ConservatorCredentials

@click.command()
@click.argument('collection_path')
@click.argument('local_folder')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-d', '--include_datasets', help="upload datasets", is_flag=True)
@click.option('-i', '--include_media', help="upload images / videos", is_flag=True)
@click.option('-m', '--include_video_metadata', help="upload video metadata", is_flag=True)
@click.option('-a', '--include_associated_files', help="upload associated files", is_flag=True)
@click.option('-c', '--create', help="create collection if it doesn't exist", is_flag=True)

def upload_collection_main(collection_path, local_folder,
                                email,
                                conservator_token,
                                include_datasets,
                                include_media,
                                include_video_metadata,
                                include_associated_files,
                                create):
    """
    This script recursively uploads local folder to given conservator path.
    Folder is uploaded with the same name that is on disk.
    Toplevel of conservator path is expected to be an existing project.
    """
    project_path = "/" + collection_path.split("/")[1]
    data = fca.get_collection_by_path(project_path, conservator_token)
    if not data:
        print("Project {} not found!".format(project_path))
        exit()

    credentials = ConservatorCredentials(email, conservator_token)
    collection = Collection.create(collection_path, credentials,
                                   parent_folder=local_folder, create_nonexistent=create)
    collection.upload_collections_recursively(include_datasets, include_video_metadata, include_associated_files, include_media)

if __name__ == "__main__":
    upload_collection_main()
