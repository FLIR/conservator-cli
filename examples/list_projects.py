from conservator import Conservator, Credentials
from conservator.util import to_clean_string

conservator = Conservator(Credentials.default(), "https://flirconservator.com/graphql")

projects = conservator.projects.all()

for index, project in enumerate(projects):
    print("Project", index)
    print(to_clean_string(project))

