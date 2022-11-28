"""
Example code for populating dataset fields
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Let's get the first dataset related to ADAS:
adas_dataset = conservator.datasets.search("ADAS").including("id").first()
print(adas_dataset)

# The `populate` function will accept:
#     A string (representing the name of a field)
#     A list of strings (representing multiple field names)
#     A FieldsRequest object (see e.g. examples/list_dataset_frames.py for details)
# Say we now want to query for the name:
adas_dataset.populate("name")
print(adas_dataset)

# Now we want all default fields:
adas_dataset.populate()
print(adas_dataset)

# There is also a `populate_all` method, which is equivalent
# to calling `populate` with no arguments
adas_dataset.populate_all()
print(adas_dataset)
