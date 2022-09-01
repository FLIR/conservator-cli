import os
import pytest

from FLIR.conservator.util import md5sum_file


@pytest.mark.usefixtures("tmp_cwd")
def test_media_file_locker(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)

    image = conservator.images.all().first()
    image.populate("file_locker_files")
    assert len(image.file_locker_files) == 0

    image.download_associated_files(".")
    assert os.path.exists("associated_files")
    assert os.path.isdir("associated_files")
    assert len(os.listdir("associated_files")) == 0
    path = test_data / "txt" / "lorem.txt"
    image.upload_associated_file(path)
    image.populate("file_locker_files")
    assert len(image.file_locker_files) == 1
    assert image.file_locker_files[0].name == "lorem.txt"

    image = conservator.images.all().first()
    image.download_associated_files(".")
    assert len(os.listdir("associated_files")) == 1
    assert os.path.exists("associated_files/lorem.txt")
    assert os.path.isfile("associated_files/lorem.txt")
    assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    image = conservator.images.all().first()
    image.remove_associated_file("lorem.txt")
    image.populate("file_locker_files")
    # But now that it has files, it's not null it's an empty list.
    assert len(image.file_locker_files) == 0


@pytest.mark.usefixtures("tmp_cwd")
def test_dataset_file_locker(conservator, test_data):
    new_dset = conservator.datasets.create("Test dataset")
    assert new_dset.wait_for_dataset_commit()

    dataset = conservator.datasets.all().first()
    dataset.populate("file_locker_files")
    assert len(dataset.file_locker_files) == 0

    dataset = conservator.datasets.all().first()
    dataset.download_associated_files(".")
    assert os.path.exists("associated_files")
    assert os.path.isdir("associated_files")
    assert len(os.listdir("associated_files")) == 0

    path = test_data / "txt" / "lorem.txt"
    dataset = conservator.datasets.all().first()
    dataset.upload_associated_file(path)
    dataset.populate("file_locker_files")
    assert len(dataset.file_locker_files) == 1
    assert dataset.file_locker_files[0].name == "lorem.txt"

    dataset.download_associated_files(".")
    assert len(os.listdir("associated_files")) == 1
    assert os.path.exists("associated_files/lorem.txt")
    assert os.path.isfile("associated_files/lorem.txt")
    assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    dataset = conservator.datasets.all().first()
    dataset.remove_associated_file("lorem.txt")
    dataset.populate("file_locker_files")
    assert len(dataset.file_locker_files) == 0


@pytest.mark.usefixtures("tmp_cwd")
def test_collection_file_locker(conservator, test_data):
    conservator.collections.create_from_remote_path("/Test")

    collection = conservator.collections.all().first()
    collection.populate("file_locker_files")
    assert len(collection.file_locker_files) == 0

    collection = conservator.collections.all().first()
    collection.download_associated_files(".")
    assert os.path.exists("associated_files")
    assert os.path.isdir("associated_files")
    assert len(os.listdir("associated_files")) == 0

    path = test_data / "txt" / "lorem.txt"
    collection = conservator.collections.all().first()
    collection.upload_associated_file(path)
    collection.populate("file_locker_files")
    assert len(collection.file_locker_files) == 1
    assert collection.file_locker_files[0].name == "lorem.txt"

    collection.download_associated_files(".")
    assert len(os.listdir("associated_files")) == 1
    assert os.path.exists("associated_files/lorem.txt")
    assert os.path.isfile("associated_files/lorem.txt")
    assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    collection = conservator.collections.all().first()
    collection.remove_associated_file("lorem.txt")
    collection.populate("file_locker_files")
    assert len(collection.file_locker_files) == 0
