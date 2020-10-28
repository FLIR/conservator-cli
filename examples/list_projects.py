from conservator import Conservator
from conservator.util import to_clean_string

conservator = Conservator.default()

# count projects:
print(conservator.projects.count())

# count projects with cars:
print(len(conservator.projects.search("adas")))

projects = conservator.projects.all().with_fields("name", "created_by_name")


# list the name and creator of all projects
for index, project in enumerate(projects):
    print("Project", index)
    print(to_clean_string(project))


projects_list = list(projects)
last_project = projects_list[-1]
print("Problematic fields are automatically excluded:")
last_project.populate_all()
print("All information about the last project:")
print(to_clean_string(last_project))
