from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Since we only care about the id and name,
# We should query for only them:
for dataset in conservator.datasets.search("ADAS").including("name", "id"):
    print(dataset.id, dataset.name)
