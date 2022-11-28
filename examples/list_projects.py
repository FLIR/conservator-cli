"""
Retrieves all projects, and prints their names and IDs
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Query all default fields:
# Default fields are configured for each type in
# FLIR/conservator/fields_manager.py
# Loading all default fields for a project used to be significantly
# slower before the data was denormalized
print("SLOWER WAY:")
for project in conservator.projects.all():
    print(project.id, project.name)

# It is recommended that you use `including` to retrieve
# only the fields you need
# Since we only care about the id and name,
# we should query for only them:
print("FASTER WAY:")
for project in conservator.projects.all().including("name", "id"):
    print(project.id, project.name)
