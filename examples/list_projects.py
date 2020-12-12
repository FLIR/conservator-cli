from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Query all fields:
# Notice there are errors, and the query needs to be repeated a few times.
# It also takes a long time to finally execute.
# This is not the recommended way to do a query (unless you actually want
# all fields).
for project in conservator.projects.all():
    print(project.id, project.name)

# Since we only care about the id and name,
# We should query for only them (this will take less than a second):
for project in conservator.projects.all().including_fields("name", "id"):
    print(project.id, project.name)
