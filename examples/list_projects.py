from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Query all default fields:
# Notice this takes a long time to finish.
# This is not the recommended way to do a query (unless you actually want
# all default fields).
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
