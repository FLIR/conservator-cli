import logging

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level=logging.DEBUG)
conservator = Conservator.default()

test_collection = conservator.collections.search("AndresTest").including("id").first()
test_collection.upload_associated_file("/tmp/TESTING")

test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.upload_associated_file("/tmp/TESTING")

test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.upload_associated_file("/tmp/TESTING")
