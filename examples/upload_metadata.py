"""
Shows how to upload a metadata file for a dataset or image
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Upload metadata to a dataset
test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.upload_metadata("/tmp/test321-MISC.json")

# Upload metadata to an image
test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.upload_metadata("/tmp/kyle.json")
