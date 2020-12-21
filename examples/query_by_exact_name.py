from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

project_name = "ADAS"

# The "name" field is searched by default, but we need to add a filter
# to make sure that the name is an exact match. Searches only check for
# substring containment, so searching "ADAS" would match "ADAS"
# and also something like "ADAS External".

# With filtered_by, we make sure to only return projects where the name is
# an exact match.
print("Normal search:")
results = conservator.projects.search(project_name, fields="name").filtered_by(
    name=project_name
)
for project in results:
    assert project.name == project_name
    print(project)


# We could also slightly speed up the query using Conservator's Advanced
# Search syntax. We can specify which field to search in the search text:
print()
print("Search by name field only:")
results = conservator.projects.search(
    f'name:"{project_name}"', fields="name"
).filtered_by(name=project_name)
for project in results:
    assert project.name == project_name
    print(project)

# The above is a common pattern, so it's been added as a function on
# SearchableTypeManager. Notice: the "name" field must be included in
# the requested fields.
print()
print("Using built-in by_exact_name")
results = conservator.projects.by_exact_name(project_name, fields="name")
for project in results:
    assert project.name == project_name
    print(project)
