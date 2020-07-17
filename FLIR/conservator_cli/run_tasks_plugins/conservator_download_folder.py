import os
from FLIR.conservator_cli.lib import graphql_api as fca
from FLIR.conservator_cli.lib.fs_collection import Collection

import blessed

t = blessed.Terminal()

def conservator_download_folder(credentials, local_folder, conservator_folder, 
                                include_datasets=False, include_video_metadata=False, 
                                include_associated_files=False, include_media=False,
                                delete=False, task=None):
    try:
        collection = Collection.create(conservator_folder, credentials, parent_folder=local_folder)
        collection.download_collections_recursively(include_datasets, include_video_metadata, 
                                                    include_associated_files, include_media, delete)

        return True
    except Exception as e:
        print(e)
        return False

exports = [conservator_download_folder]
