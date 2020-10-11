from conservator import Conservator, Credentials
from conservator.util import to_clean_string

conservator = Conservator(Credentials.default(), "https://flirconservator.com/graphql")

datasets = conservator.datasets.all()

for index, dataset in enumerate(datasets):
    print("Dataset", index)
    print(to_clean_string(dataset))

