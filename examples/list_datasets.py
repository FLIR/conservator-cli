from conservator import Conservator
from conservator.util import to_clean_string

conservator = Conservator.default()

datasets = conservator.datasets.all().with_fields("repository.master")

for index, dataset in enumerate(datasets):
    print("Dataset", index)
    print(to_clean_string(dataset))

