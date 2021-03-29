import pytest
from FLIR.conservator.wrappers.collection import RemotePathExistsException


def test_create_project(conservator):
    # TODO: having an exclamation point in the name breaks search.
    project = conservator.projects.create("My Project")
    assert project is not None
    assert project.id is not None
    assert project.name == "My Project"


def test_get_project(conservator):
    project = conservator.projects.create("My Project")
    project_id = project.id

    project_from_id = conservator.projects.from_id(project_id)
    assert project_from_id is not None
    project_from_id.populate("name")
    assert project_from_id.name is not None
    assert project_from_id.name == project.name


def test_id_exists(conservator):
    project = conservator.projects.create("My Project")
    assert conservator.projects.id_exists(project.id)


def test_delete_project(conservator):
    project = conservator.projects.create("My Project")
    assert conservator.projects.id_exists(project.id)

    project.delete()
    assert not conservator.projects.id_exists(project.id)


def test_search(conservator):
    project1 = conservator.projects.create("First Project")
    project2 = conservator.projects.create("Second Project")
    project_ids = {project1.id, project2.id}

    assert conservator.projects.count("First") == 1
    fetched_projects = conservator.projects.search("First")
    assert len(fetched_projects) == 1
    assert project1.id == fetched_projects.first().id

    assert conservator.projects.count("Second") == 1
    fetched_projects = conservator.projects.search("Second")
    assert len(fetched_projects) == 1
    assert project2.id == fetched_projects.first().id

    assert conservator.projects.count("Project") == 2
    fetched_projects = conservator.projects.search("Project")
    assert len(fetched_projects) == 2
    assert set(project.id for project in fetched_projects) == project_ids

    assert conservator.projects.count("Doesn't exist") == 0
    fetched_projects = conservator.projects.search("Doesn't exist")
    assert len(fetched_projects) == 0
    assert fetched_projects.first() is None


def test_by_exact_name(conservator):
    project = conservator.projects.create("Some project name")
    _ = conservator.projects.create("Similar project name")

    # Not exact match
    fetched = conservator.projects.by_exact_name("project name")
    assert len(fetched) == 0
    assert fetched.first() is None

    fetched = conservator.projects.by_exact_name("Some project name")
    assert len(fetched) == 1
    assert fetched.first().id == project.id


def test_duplicate_name(conservator):
    conservator.projects.create("Project")
    with pytest.raises(RemotePathExistsException):
        conservator.projects.create("Project")


def test_reuse_name(conservator):
    project = conservator.projects.create("Project")
    project.delete()
    # Reuse is ok as long as deleted.
    new_project = conservator.projects.create("Project")
    assert new_project.id != project.id
    # Not deleted--not ok.
    with pytest.raises(RemotePathExistsException):
        conservator.projects.create("Project")


def test_many_projects(conservator):
    NUM_PROJECTS = 50
    project_ids = set()
    for i in range(NUM_PROJECTS):
        project = conservator.projects.create(f"Project #{i}")
        assert project is not None
        assert project.id is not None
        project_ids.add(project.id)
    assert len(project_ids) == NUM_PROJECTS

    assert conservator.projects.count_all() == NUM_PROJECTS
    all_projects = list(conservator.projects.all())
    fetched_ids = set(project.id for project in all_projects)

    assert len(fetched_ids) == NUM_PROJECTS
    assert project_ids == fetched_ids
