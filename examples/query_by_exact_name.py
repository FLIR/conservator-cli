"""
Example code for querying projects by exact name
"""
from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

PROJECT_NAME = "ADAS"

# The "name" field is searched by default, but we need to add a filter
# to make sure that the name is an exact match. Searches only check for
# substring containment, so searching "ADAS" would match "ADAS"
# and also something like "ADAS External".

# With filtered_by, we make sure to only return projects where the name is
# an exact match.
print("Normal search:")
results = conservator.projects.search(PROJECT_NAME, fields="name").filtered_by(
    name=PROJECT_NAME
)
for project in results:
    assert project.name == PROJECT_NAME
    print(project)


# We could also slightly speed up the query using Conservator's Advanced
# Search syntax. We can specify which field to search in the search text:
print()
print("Search by name field only:")
results = conservator.projects.search(
    f'name:"{PROJECT_NAME}"', fields="name"
).filtered_by(name=PROJECT_NAME)
for project in results:
    assert project.name == PROJECT_NAME
    print(project)

# The above is a common pattern, so it's been added as a function on
# SearchableTypeManager.
print()
print("Using built-in by_exact_name:")
results = conservator.projects.by_exact_name(PROJECT_NAME, fields="name")
for project in results:
    assert project.name == PROJECT_NAME
    print(project)
