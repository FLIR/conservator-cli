from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Cloning from a known ID:
known_dataset = conservator.datasets.from_id("wJQfFkgNDpTqTQGv3")
known_dataset.clone("~/datasets/")

# Cloning can of course be done from any instance--as long as its
# ID is known. Cloning the first from a search:
deer_dataset = conservator.datasets.search("deer").with_fields("id").first()
deer_dataset.clone("~/datasets/")
