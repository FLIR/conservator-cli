from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Query all fields:
# Notice there are errors, and the query needs to be repeated a few times.
# It also takes a long time to finally execute.
# This is not the recommended way to do a query (unless you actually want
# all fields).
print("SLOWER WAY:")
for project in conservator.projects.all():
    print(project.id, project.name)

print()
print()

# Since we only care about the id and name,
# We should query for only them (this will take less than a second):
print("FASTER WAY:")
for project in conservator.projects.all().including("name", "id"):
    print(project.id, project.name)
