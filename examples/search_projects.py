from FLIR.conservator.conservator import Conservator

conservator = Conservator.default()

for project in conservator.projects.search("ADAS").including_fields("name"):
    print(project.id, project.name)

