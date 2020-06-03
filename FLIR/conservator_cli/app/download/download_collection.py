#!/usr/bin/env python3
import click
import json
import os
import subprocess
import shutil

from FLIR.conservator_cli.lib import graphql_api as fca
from FLIR.conservator_cli.lib.fs_collection import Collection
from FLIR.conservator_cli.lib.conservator_credentials import ConservatorCredentials

@click.command()
@click.argument('collection_path')
@click.argument('local_folder')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-d', '--include_datasets', help="download datasets", is_flag=True)
@click.option('-i', '--include_media', help="download images / videos", is_flag=True)
@click.option('-m', '--include_video_metadata', help="download video metadata", is_flag=True)
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
@click.option('-o', '--delete', help="remove local files not present in conservator", is_flag=True)

def download_collection_main(collection_path, local_folder,
                                email,
                                conservator_token,
                                include_datasets,
                                include_media,
                                include_video_metadata,
                                include_associated_files,
                                delete):
    data = fca.get_collection_by_path(collection_path, conservator_token)
    if not data:
        print("Collection {} not found!".format(collection_path))
        exit()
    credentials = ConservatorCredentials(email, conservator_token)
    collection = Collection.create(collection_path, credentials, parent_folder=local_folder)
    collection.download_collections_recursively(include_datasets, include_video_metadata, include_associated_files, include_media, delete)

if __name__ == "__main__":
    download_collection_main()
