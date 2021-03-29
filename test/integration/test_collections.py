import pytest

from FLIR.conservator.wrappers.collection import RemotePathExistsException


def test_create_child(conservator):
    project = conservator.projects.create("Root")
    parent_collection = project.root_collection
    collection = parent_collection.create_child("My child collection")

    assert collection is not None
    assert collection.name == "My child collection"
    assert collection.path == "/Root/My child collection"
    parent_collection.populate("children")
    children = parent_collection.children
    assert len(children) == 1
    assert children[0].id == collection.id


def test_create_from_parent_id(conservator):
    project = conservator.projects.create("Root")
    parent_collection = project.root_collection
    collection = conservator.collections.create_from_parent_id(
        name="My child collection", parent_id=parent_collection.id
    )

    assert collection is not None
    assert collection.name == "My child collection"
    assert collection.path == "/Root/My child collection"
    parent_collection.populate("children")
    children = parent_collection.children
    assert len(children) == 1
    assert children[0].id == collection.id


def test_get_child(conservator):
    project = conservator.projects.create("Root")
    parent_collection = project.root_collection
    collection = parent_collection.create_child("My child collection")

    child = parent_collection.get_child("My child collection")
    assert child is not None
    assert child.id == collection.id


def test_get_child_make_if_no_exist(conservator):
    project = conservator.projects.create("Root")
    parent_collection = project.root_collection

    child = parent_collection.get_child("My child collection", make_if_no_exists=True)
    assert child is not None
    assert child.name == "My child collection"
    assert child.path == "/Root/My child collection"

    fetched_child = parent_collection.get_child("My child collection")
    assert fetched_child is not None
    assert fetched_child.id == child.id

    parent_collection.populate("children")
    children = parent_collection.children
    assert len(children) == 1
    assert children[0].id == child.id


def test_create_root(conservator):
    root_collection = conservator.collections.create_root("Root")
    assert root_collection is not None
    assert root_collection.path == "/Root"
    assert root_collection.name == "Root"

    # Should also create a project.
    project = conservator.projects.by_exact_name("Root").first()
    assert project is not None
    assert project.name == "Root"
    project.populate("root_collection")
    assert project.root_collection.id == root_collection.id


def test_create_root_existing(conservator):
    conservator.collections.create_root("Root name")
    with pytest.raises(RemotePathExistsException):
        conservator.collections.create_root("Root name")


def test_create_from_remote_path(conservator):
    collection_a = conservator.collections.create_from_remote_path(
        "/Some/Super/Long/Path"
    )
    assert collection_a is not None
    assert collection_a.name == "Path"
    assert collection_a.path == "/Some/Super/Long/Path"

    collection_b = conservator.collections.create_from_remote_path(
        "/Some/Other/Long/Path"
    )
    assert collection_b is not None
    assert collection_b.name == "Path"
    assert collection_b.path == "/Some/Other/Long/Path"
    assert collection_a.id != collection_b.id


def test_create_from_remote_path_existing(conservator):
    PATH = "/Some Collection's/Very/Super/Long/Path"
    collection = conservator.collections.create_from_remote_path(PATH)
    assert collection.path == PATH
    with pytest.raises(RemotePathExistsException):
        conservator.collections.create_from_remote_path(PATH)


def test_from_remote_path(conservator):
    pass


def test_from_remote_path_make_if_no_exist(conservator):
    pass


def test_recursively_get_children(conservator):
    pass


def test_get_images(conservator):
    # TODO once upload/download done
    pass


def test_recursively_get_images(conservator):
    # TODO once upload/download done
    pass


def test_get_videos(conservator):
    # TODO once upload/download done
    pass


def test_recursively_get_videos(conservator):
    # TODO once upload/download done
    pass


def test_get_media(conservator):
    # TODO once upload/download done
    pass


def test_recursively_get_media(conservator):
    # TODO once upload/download done
    pass


def test_get_datasets(conservator):
    # TODO once upload/download done
    pass


def test_remove_media(conservator):
    # TODO once upload/download done
    pass


def test_delete(conservator):
    pass


def test_download_metadata(conservator):
    # TODO once upload/download done
    pass


def test_download_media(conservator):
    # TODO once upload/download done
    pass


def test_download_videos(conservator):
    # TODO once upload/download done
    pass


def test_download_images(conservator):
    # TODO once upload/download done
    pass


def test_download_datasets(conservator):
    # TODO once upload/download done
    pass
