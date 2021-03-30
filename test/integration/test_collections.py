import pytest
from FLIR.conservator.connection import ConservatorGraphQLServerError

from FLIR.conservator.wrappers.collection import RemotePathExistsException, InvalidRemotePathException


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


@pytest.mark.parametrize(
    "path",
    [
        "/Root Collection",
        "/Long/Collection/Path",
        "/Very/Long/Collection/Path/A/B/C/D/E/F/G/H/I/J",
    ],
)
def test_from_remote_path(conservator, path):
    collection = conservator.collections.create_from_remote_path(path)
    assert collection is not None
    assert collection.path == path

    fetched_collection = conservator.collections.from_remote_path(path)
    assert fetched_collection is not None
    assert fetched_collection.id == collection.id
    assert fetched_collection.path == path


@pytest.mark.parametrize(
    "path",
    [
        "Root Collection",
        "Long/Collection/Path",
        "Very/Long/Collection/Path/A/B/C/D/E/F/G/H/I/J",
    ],
)
def test_from_remote_path_no_slash(conservator, path):
    collection = conservator.collections.create_from_remote_path(path)
    assert collection is not None
    assert collection.path == "/" + path

    fetched_collection = conservator.collections.from_remote_path(path)
    assert fetched_collection is not None
    assert fetched_collection.id == collection.id
    assert fetched_collection.path == "/" + path


@pytest.mark.parametrize(
    "path",
    [
        "/Root Collection",
        "/Long/Collection/Path",
        "/Very/Long/Collection/Path/A/B/C/D/E/F/G/H/I/J",
    ],
)
def test_from_remote_path_make_if_no_exist(conservator, path):
    collection = conservator.collections.from_remote_path(path, make_if_no_exist=True)
    assert collection is not None
    assert collection.id == collection.id

    fetched_collection = conservator.collections.from_remote_path(path)
    assert fetched_collection is not None
    assert fetched_collection.id == collection.id
    assert fetched_collection.path == path


def test_recursively_get_children_broad(conservator):
    PATHS = [
        "/Root/Child",
        "/Root/Sibling",
        "/Root/Grand",
        "/Root/Grand/Child",
        "/Root/Grand/Grand",
        "/Root/Grand/Grand/Child",
        "/Root/Grand/Grand/Sibling",
    ]
    root_collection = conservator.collections.create_root("Root")
    for path in PATHS:
        conservator.collections.create_from_remote_path(path)

    children = list(root_collection.recursively_get_children(fields="path"))
    assert len(children) == len(PATHS)
    child_paths = [child.path for child in children]
    assert set(child_paths) == set(PATHS)

    children_and_self = list(root_collection.recursively_get_children(fields="path", include_self=True))
    assert len(children_and_self) == len(PATHS) + 1


def test_recursively_get_children_deep(conservator):
    DEPTH = 20
    root_collection = conservator.collections.create_root("Root")
    conservator.collections.create_from_remote_path("/Root" + "/Child" * DEPTH)

    children = list(root_collection.recursively_get_children(fields="path"))
    assert len(children) == DEPTH

    children_and_self = list(root_collection.recursively_get_children(fields="path", include_self=True))
    assert len(children_and_self) == DEPTH + 1


def test_delete_root(conservator):
    root_collection = conservator.collections.create_root("Root")
    assert root_collection is not None

    root_collection.delete()
    assert not conservator.collections.id_exists(root_collection.id)
    assert conservator.collections.count_all() == 0


def test_delete_child(conservator):
    collection = conservator.collections.create_from_remote_path("/My/Complicated/Collection/Path")
    assert collection is not None

    collection.delete()
    assert not conservator.collections.id_exists(collection.id)

    parent = conservator.collections.from_remote_path("/My/Complicated/Collection", fields="children.id")
    assert parent is not None
    assert len(parent.children) == 0

    root = conservator.collections.from_remote_path("/My")
    assert len(list(root.recursively_get_children())) == 2


def test_delete_parent(conservator):
    conservator.collections.create_from_remote_path("/My/Complicated/Collection/Path")

    parent = conservator.collections.from_remote_path("/My/Complicated/Collection")
    with pytest.raises(ConservatorGraphQLServerError):
        # You can't delete a collection that has children
        parent.delete()


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
