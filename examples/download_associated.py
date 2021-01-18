import logging

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

logging.basicConfig(level=logging.DEBUG)
conservator = Conservator.default()

test_collection = conservator.collections.search("AndresTest").including("id").first()
test_collection.download_associated_files("/tmp/dl-collection")

test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.download_associated_files("/tmp/dl-dataset")

test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.download_associated_files("/tmp/dl-image")
