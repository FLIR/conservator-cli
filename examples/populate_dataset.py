from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.types import Dataset

conservator = Conservator.default()

# Let's get the first dataset related to ADAS:
adas_dataset = conservator.datasets.search("ADAS").including_fields("id").first()
print(adas_dataset)

# Say we now want to query for the name:
fields = FieldsRequest()
fields.include_field("name")
adas_dataset.populate(fields)
print(adas_dataset)

# Now we want everything:
adas_dataset.populate_all()
print(adas_dataset)
