import os
from FLIR.conservator_cli.lib import graphql_api as fca
from FLIR.conservator_cli.lib.fs_collection import Collection

import blessed

t = blessed.Terminal()

def conservator_upload_folder(credentials, local_folder, conservator_folder, 
                                include_datasets=False, include_video_metadata=False, 
                                include_associated_files=False, include_media=False,
                                create=False, task=None):
    try:
        collection = Collection.create(conservator_folder, credentials, 
                                       parent_folder=local_folder, create_nonexistent=create)
        collection.upload_collections_recursively(include_datasets, include_video_metadata, 
                                                  include_associated_files, include_media)

        return True
    except Exception as e:
        print(e)
        return False

exports = [conservator_upload_folder]
