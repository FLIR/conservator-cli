from conservator import Conservator, Config
from conservator.util import to_clean_string

conservator = Conservator(Config.default(), "https://flirconservator.com/graphql")

datasets = conservator.datasets.all()

for index, dataset in enumerate(datasets):
    print("Dataset", index)
    print(to_clean_string(dataset))

