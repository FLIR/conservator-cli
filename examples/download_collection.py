#!/usr/bin/env python3
import click

from pyconservator.legacy import graphql_api as fca
from pyconservator.legacy.conservator_credentials import ConservatorCredentials
from pyconservator.legacy.fs_collection import Collection


@click.command()
@click.argument('collection_path')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-d', '--include_datasets', help="download datasets", is_flag=True)
@click.option('-i', '--include_images', help="download images", is_flag=True)
@click.option('-m', '--include_video_metadata', help="download video metadata", is_flag=True)
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
@click.option('-o', '--delete', help="remove local files not present in conservator", is_flag=True)
def download_collection_main(collection_path,
                             email,
                             conservator_token,
                             include_datasets,
                             include_images,
                             include_video_metadata,
                             include_associated_files,
                             delete):
    print(collection_path)
    data = fca.get_collection_by_path(collection_path, conservator_token)
    if not data:
        print("Collection {} not found!".format(collection_path))
        exit()
    credentials = ConservatorCredentials(email, conservator_token)
    collection = Collection.create(collection_path, credentials)
    collection.download_collections_recursively(include_datasets, include_video_metadata, include_associated_files,
                                                include_images, delete)


if __name__ == "__main__":
    download_collection_main()
