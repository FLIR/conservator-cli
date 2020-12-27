from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

conservator = Conservator.default()

# Let's get the first dataset related to ADAS:
adas_dataset = conservator.datasets.search("ADAS").including("id").first()
print(adas_dataset)

# Say we now want to query for the name:
adas_dataset.populate("name")
print(adas_dataset)

# Now we want all default fields:
adas_dataset.populate_all()
print(adas_dataset)
