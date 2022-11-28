"""
Example code for cloning a dataset
"""
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.local_dataset import LocalDataset

conservator = Conservator.default()

# Cloning from a known ID:
known_dataset = conservator.datasets.from_id("wJQfFkgNDpTqTQGv3")
known_dataset_local = LocalDataset.clone(known_dataset)

# Cloning can of course be done from any instance--as long as its
# ID is known. Cloning the first from a search:
deer_dataset = conservator.datasets.search("deer").with_fields("id").first()
deer_dataset_local = LocalDataset.clone(deer_dataset)
