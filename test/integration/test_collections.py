import json
import os

import pytest
from FLIR.conservator.connection import ConservatorGraphQLServerError

from FLIR.conservator.wrappers.collection import (
    RemotePathExistsException,
    InvalidRemotePathException,
)
from FLIR.conservator.generated.schema import Mutation, MetadataInput
from conftest import upload_media


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


def test_from_invalid_remote_raises_exception(conservator):
    with pytest.raises(InvalidRemotePathException):
        conservator.collections.from_remote_path("/Some/non-existent/Path")


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

    children_and_self = list(
        root_collection.recursively_get_children(fields="path", include_self=True)
    )
    assert len(children_and_self) == len(PATHS) + 1


def test_recursively_get_children_deep(conservator):
    DEPTH = 20
    root_collection = conservator.collections.create_root("Root")
    conservator.collections.create_from_remote_path("/Root" + "/Child" * DEPTH)

    children = list(root_collection.recursively_get_children(fields="path"))
    assert len(children) == DEPTH

    children_and_self = list(
        root_collection.recursively_get_children(fields="path", include_self=True)
    )
    assert len(children_and_self) == DEPTH + 1


def test_delete_root(conservator):
    root_collection = conservator.collections.create_root("Root")
    assert root_collection is not None

    root_collection.delete()
    assert not conservator.collections.id_exists(root_collection.id)
    assert conservator.collections.count_all() == 0


def test_delete_child(conservator):
    collection = conservator.collections.create_from_remote_path(
        "/My/Complicated/Collection/Path"
    )
    assert collection is not None

    collection.delete()
    assert not conservator.collections.id_exists(collection.id)

    parent = conservator.collections.from_remote_path(
        "/My/Complicated/Collection", fields="children.id"
    )
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


def test_remove_media(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/Some/Collection")
    local_path = test_data / "jpg" / "surfers_0.jpg"
    media_id = conservator.media.upload(local_path, collection=collection)
    conservator.media.wait_for_processing(media_id)
    assert len(list(collection.get_media())) == 1

    collection.remove_media(media_id)

    assert len(list(collection.get_media())) == 0


def test_create_dataset(conservator):
    collection = conservator.collections.create_from_remote_path("/Some/Collection")

    dataset = collection.create_dataset("My dataset")

    assert conservator.datasets.id_exists(dataset.id)
    dataset.populate("collections")  # a list of Collection IDs
    assert len(dataset.collections) == 1
    assert dataset.collections[0] == collection.id


def test_get_datasets(conservator):
    collection = conservator.collections.create_from_remote_path("/Some/Collection")
    dataset_1 = collection.create_dataset("My first dataset")
    dataset_2 = collection.create_dataset("My second dataset")

    datasets = collection.get_datasets()

    assert len(datasets) == 2
    dataset_ids = [dataset.id for dataset in datasets]
    assert dataset_1.id in dataset_ids
    assert dataset_2.id in dataset_ids


def test_download_datasets(conservator, tmp_cwd):
    collection = conservator.collections.create_from_remote_path("/Some/Collection")
    dataset_1 = collection.create_dataset("My first dataset")

    collection.download_datasets(".")

    assert os.path.exists("My first dataset")
    assert os.path.isdir("My first dataset")
    local_dataset = conservator.datasets.from_local_path("My first dataset")
    assert local_dataset.id == dataset_1.id


class TestCollectionsWithMedia:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_0.jpg", "/Cats", None),
            (test_data / "jpg" / "cat_1.jpg", "/Cats", None),
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "Named cat pic.jpg"),
            (test_data / "jpg" / "cat_0.jpg", "/Animals/Cats", None),
            (test_data / "jpg" / "cat_1.jpg", "/Animals/Cats", None),
            (test_data / "jpg" / "cat_2.jpg", "/Animals/Cats", "Named cat pic.jpg"),
            (test_data / "jpg" / "dog_0.jpg", "/Animals/Dogs", None),
            (test_data / "jpg" / "dog_1.jpg", "/Animals/Dogs", None),
            (test_data / "jpg" / "dog_2.jpg", "/Animals/Dogs", "Named dog pic.jpg"),
            (test_data / "jpg" / "bird_0.jpg", "/Animals/Birds", None),
            (test_data / "jpg" / "aerial_0.jpg", "/Flight", None),
            (test_data / "jpg" / "drone_0.jpg", "/Flight", None),
            (test_data / "mp4" / "adas_thermal.mp4", "/Flight/Thermal", None),
            (
                test_data / "mp4" / "adas_thermal.mp4",
                "/Flight/Thermal",
                "Same video but named.mp4",
            ),
        ]
        upload_media(conservator, MEDIA)

    def test_get_images(self, conservator):
        collection = conservator.collections.from_remote_path("/Cats")
        images = collection.get_images()
        assert len(images) == 3

    def test_recursively_get_images(self, conservator):
        collection = conservator.collections.from_remote_path("/Animals")
        images = list(collection.recursively_get_images())
        assert len(images) == 7

    def test_recursively_get_images_includes_self(self, conservator):
        collection = conservator.collections.from_remote_path("/Animals/Dogs")
        images = list(collection.recursively_get_images())
        assert len(images) == 3

    def test_get_videos(self, conservator):
        collection = conservator.collections.from_remote_path("/Flight/Thermal")
        videos = collection.get_videos()
        assert len(videos) == 2

    def test_recursively_get_videos(self, conservator):
        collection = conservator.collections.from_remote_path("/Flight")
        videos = list(collection.recursively_get_videos())
        assert len(videos) == 2

    def test_get_media(self, conservator):
        collection = conservator.collections.from_remote_path("/Flight")
        media = list(collection.get_media())
        assert len(media) == 2  # only two media directly in /Flight

    def test_recursively_get_media(self, conservator):
        collection = conservator.collections.from_remote_path("/Flight")
        media = list(collection.recursively_get_media())
        assert len(media) == 4  # 2 images, 2 videos

    def test_download_metadata(self, conservator, tmp_cwd):
        collection = conservator.collections.from_remote_path("/Cats")
        collection.download_metadata("./cats")
        assert os.path.exists("./cats/media_metadata")
        files = os.listdir("./cats/media_metadata")
        assert len(files) == 3
        assert "cat_0.json" in files
        assert "cat_1.json" in files
        assert "Named cat pic.json" in files
        # Sanity check that we actually downloaded JSON, with correct ID
        with open("cats/media_metadata/Named cat pic.json") as o:
            data = json.load(o)
            media_id = data["videos"][0]["id"]
            assert conservator.images.id_exists(media_id)
            media = conservator.images.from_id(media_id)
            media.populate()
            assert media.name == "Named cat pic.jpg"

    def test_download_images(self, conservator, tmp_cwd):
        collection = conservator.collections.from_remote_path("/Cats")
        collection.download_images("./images/")

        assert len(os.listdir("images")) == 3
        assert os.path.exists("images/cat_0.jpg")
        assert os.path.exists("images/cat_1.jpg")
        assert os.path.exists("images/Named cat pic.jpg")

    def test_download_videos(self, conservator, tmp_cwd):
        collection = conservator.collections.from_remote_path("/Flight/Thermal")
        collection.download_videos("./videos/")

        assert len(os.listdir("videos")) == 2
        assert os.path.exists("videos/adas_thermal.mp4")
        assert os.path.exists("videos/Same video but named.mp4")

    def test_download_media(self, conservator, tmp_cwd):
        collection = conservator.collections.from_remote_path("/Flight")
        collection.download_media("./media/")

        assert len(os.listdir("media")) == 2
        assert os.path.exists("media/aerial_0.jpg")
        assert os.path.exists("media/drone_0.jpg")

    def test_download_recursively(self, conservator, tmp_cwd):
        collection = conservator.collections.from_remote_path("/Animals")

        collection.download(
            include_media=True,
            recursive=True,
        )

        assert len(os.listdir("Animals/")) == 3
        assert len(os.listdir("Animals/Cats/")) == 3
        assert os.path.exists("Animals/Cats/cat_0.jpg")
        assert os.path.exists("Animals/Cats/cat_1.jpg")
        assert os.path.exists("Animals/Cats/Named cat pic.jpg")
        assert len(os.listdir("Animals/Dogs/")) == 3
        assert os.path.exists("Animals/Dogs/dog_0.jpg")
        assert os.path.exists("Animals/Dogs/dog_1.jpg")
        assert os.path.exists("Animals/Dogs/Named dog pic.jpg")
        assert len(os.listdir("Animals/Birds")) == 1
        assert os.path.exists("Animals/Birds/bird_0.jpg")
