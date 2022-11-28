"""
Example code to demonstrate uploading an associated file
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()


# Upload an associated file to a collection
test_collection = conservator.collections.search("AndresTest").including("id").first()
test_collection.upload_associated_file("/tmp/TESTING")

# Upload an associated file to a dataset
test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.upload_associated_file("/tmp/TESTING")

# Upload an associated file to an image
test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.upload_associated_file("/tmp/TESTING")
