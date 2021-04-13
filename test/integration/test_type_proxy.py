from FLIR.conservator.wrappers import Project


def test_has_field(conservator):
    instance = conservator.projects.create("Test")

    # This test is dependent on default fields.
    assert instance.has_field("id")
    assert instance.has_field("name")
    assert instance.has_field("root_collection")
    assert instance.has_field("root_collection.id")
    assert instance.has_field("root_collection.name")
    assert not instance.has_field("non_existent_field")
    assert not instance.has_field("root_collection.non_existent_field")
    assert not instance.has_field("a.b.c.d")
    assert not instance.has_field("id.bad")

    # Try something we can populate
    assert not instance.has_field("acl")
    instance.populate("acl")
    assert instance.has_field("acl")


def test_from_id(conservator):
    project_id = conservator.projects.create("Test").id

    instance = Project.from_id(conservator, project_id)
    assert instance.id == project_id


def test_from_json(conservator):
    instance = Project.from_json(conservator, {"name": "foo"})
    assert instance.name == "foo"


def test_to_json(conservator):
    JSON = {"name": "bar"}
    instance = Project.from_json(conservator, JSON)

    assert instance.to_json() == JSON


def test_list_to_json(conservator):
    root = conservator.collections.create_from_remote_path("/Root")
    root.populate("children")

    assert root.children.to_json() == []
