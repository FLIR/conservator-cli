"""
Demonstrates some of the search functionality
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# General search will search for the provided text in
# the dataset's name, tags, or notes
for dataset in conservator.datasets.search("ADAS").including("name", "id"):
    print(dataset.id, dataset.name)

# Other, more specific search terms are available
# e.g. owner:
for dataset in conservator.datasets.search('owner:"user@example.com"').including(
    "name", "id"
):
    print(dataset.id, dataset.name)

# Creation date:
for dataset in conservator.datasets.search('before:"2022-01-31"').including(
    "name", "id"
):
    print(dataset.id, dataset.name)

for dataset in conservator.datasets.search('after:"2022-01-31"').including(
    "name", "id"
):
    print(dataset.id, dataset.name)

# Annotation label:
for dataset in conservator.datasets.search('has:"vehicle"').including("name", "id"):
    print(dataset.id, dataset.name)
