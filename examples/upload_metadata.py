import logging

from FLIR.conservator.conservator import Conservator

logging.basicConfig(level=logging.DEBUG)
conservator = Conservator.default()

test_dataset = conservator.datasets.search("test321-MISC").including("id").first()
test_dataset.upload_metadata("/tmp/test321-MISC.json")

test_image = conservator.images.search("kyle.jpg").including("id").first()
test_image.upload_metadata("/tmp/kyle.json")
