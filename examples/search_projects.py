from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

# Query all fields (this will take a few seconds):
for project in conservator.projects.search("ADAS"):
    print(project.id, project.name)

# Since we only care about the id and name,
# We could also query for only them:
for project in conservator.projects.search("ADAS").including_fields("name", "id"):
    print(project.id, project.name)

