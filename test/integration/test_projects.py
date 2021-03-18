
def test_create_project(conservator):
    PROJECT_NAME = "My Project!!!"
    project = conservator.projects.create(PROJECT_NAME)
    assert project is not None
    assert project.id is not None
    assert project.name == PROJECT_NAME


def test_delete_project(conservator):
    project = conservator.projects.create("My Project")
    assert conservator.projects.id_exists(project.id)

    project.delete()
    assert not conservator.projects.id_exists(project.id)

