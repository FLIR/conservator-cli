# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
import pytest

from FLIR.conservator.wrappers.queryable import InvalidIdException


def test_id_exists(conservator):
    project = conservator.projects.create("Project")
    assert conservator.projects.id_exists(project.id)


def test_id_no_exists(conservator):
    fake_id = conservator.generate_id()
    assert not conservator.projects.id_exists(fake_id)


def test_from_id(conservator):
    project_id = conservator.projects.create("Project").id

    project = conservator.projects.from_id(project_id)

    assert project is not None
    assert project.id == project_id


def test_from_id_invalid_raises_error(conservator):
    invalid_id = "Not an id."
    with pytest.raises(InvalidIdException):
        conservator.projects.from_id(invalid_id)


def test_from_json(conservator):
    project = conservator.projects.create("Project")

    json = project.to_json()
    instance = conservator.projects.from_json(json)

    assert instance is not None
    assert instance.id == project.id
    assert instance.name == project.name
    assert instance.to_json() == json
