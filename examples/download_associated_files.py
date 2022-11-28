"""
A brief script that provides examples of
how to download associated files from various
Conservator entities
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Download associated files from the first collection
# (i.e. a project or folder) that matches the search
# to a local folder (/tmp/dl-collection)
test_collection = conservator.collections.search("AndresTest").including("id").first()
test_collection.download_associated_files("/tmp/dl-collection")

# Download associated files from the first dataset
# that matches the search to a local folder (/tmp/dl-dataset)
test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.download_associated_files("/tmp/dl-dataset")


# Download associated files from the first image
# that matches the search to a local folder (/tmp/dl-image)
test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.download_associated_files("/tmp/dl-image")
