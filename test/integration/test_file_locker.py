import os
import pytest as pytest

from FLIR.conservator.util import md5sum_file
from conftest import upload_media


class TestFileLockerMedia:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        # File locker files for images and videos are treated the same.
        upload_media(conservator, MEDIA)

    def test_file_locker_files_start_null(self, conservator):
        image = conservator.images.all().first()
        image.populate("file_locker_files")
        # For some reason, it starts as null.
        # This behavior is unique to Image/Video.
        # JIRA Ticket CON-1472 is tracking this discrepancy.
        assert image.file_locker_files is None
        # assert len(image.file_locker_files) == 0

    def test_download_empty(self, conservator, tmp_cwd):
        image = conservator.images.all().first()
        image.download_associated_files(".")

        assert os.path.exists("associated_files")
        assert os.path.isdir("associated_files")
        assert len(os.listdir("associated_files")) == 0

    def test_upload(self, conservator, test_data):
        path = test_data / "txt" / "lorem.txt"
        image = conservator.images.all().first()
        image.upload_associated_file(path)

        image.populate("file_locker_files")
        assert len(image.file_locker_files) == 1
        assert image.file_locker_files[0].name == "lorem.txt"

    def test_download(self, conservator, tmp_cwd, test_data):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        path = test_data / "txt" / "lorem.txt"
        image = conservator.images.all().first()
        image.download_associated_files(".")

        assert len(os.listdir("associated_files")) == 1
        assert os.path.exists("associated_files/lorem.txt")
        assert os.path.isfile("associated_files/lorem.txt")

        assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    def test_remove(self, conservator):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        image = conservator.images.all().first()
        image.remove_associated_file("lorem.txt")

        image.populate("file_locker_files")
        # But now that it has files, it's not null it's an empty list.
        assert len(image.file_locker_files) == 0


class TestFileLockerDataset:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        upload_media(conservator, MEDIA)
        conservator.datasets.create("Test dataset")

    def test_file_locker_files_start_null(self, conservator):
        dataset = conservator.datasets.all().first()
        dataset.populate("file_locker_files")
        assert len(dataset.file_locker_files) == 0

    def test_download_empty(self, conservator, tmp_cwd):
        dataset = conservator.datasets.all().first()
        dataset.download_associated_files(".")

        assert os.path.exists("associated_files")
        assert os.path.isdir("associated_files")
        assert len(os.listdir("associated_files")) == 0

    def test_upload(self, conservator, test_data):
        path = test_data / "txt" / "lorem.txt"
        dataset = conservator.datasets.all().first()
        dataset.upload_associated_file(path)

        dataset.populate("file_locker_files")
        assert len(dataset.file_locker_files) == 1
        assert dataset.file_locker_files[0].name == "lorem.txt"

    def test_download(self, conservator, tmp_cwd, test_data):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        path = test_data / "txt" / "lorem.txt"
        dataset = conservator.datasets.all().first()
        dataset.download_associated_files(".")

        assert len(os.listdir("associated_files")) == 1
        assert os.path.exists("associated_files/lorem.txt")
        assert os.path.isfile("associated_files/lorem.txt")

        assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    def test_remove(self, conservator):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        dataset = conservator.datasets.all().first()
        dataset.remove_associated_file("lorem.txt")

        dataset.populate("file_locker_files")
        # But now that it has files, it's not null it's an empty list.
        assert len(dataset.file_locker_files) == 0


class TestFileLockerCollection:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        upload_media(conservator, MEDIA)

    def test_file_locker_files_start_null(self, conservator):
        collection = conservator.collections.all().first()
        collection.populate("file_locker_files")
        assert len(collection.file_locker_files) == 0

    def test_download_empty(self, conservator, tmp_cwd):
        collection = conservator.collections.all().first()
        collection.download_associated_files(".")

        assert os.path.exists("associated_files")
        assert os.path.isdir("associated_files")
        assert len(os.listdir("associated_files")) == 0

    def test_upload(self, conservator, test_data):
        path = test_data / "txt" / "lorem.txt"
        collection = conservator.collections.all().first()
        collection.upload_associated_file(path)

        collection.populate("file_locker_files")
        assert len(collection.file_locker_files) == 1
        assert collection.file_locker_files[0].name == "lorem.txt"

    def test_download(self, conservator, tmp_cwd, test_data):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        path = test_data / "txt" / "lorem.txt"
        collection = conservator.collections.all().first()
        collection.download_associated_files(".")

        assert len(os.listdir("associated_files")) == 1
        assert os.path.exists("associated_files/lorem.txt")
        assert os.path.isfile("associated_files/lorem.txt")

        assert md5sum_file("associated_files/lorem.txt") == md5sum_file(path)

    def test_remove(self, conservator):
        # !!! WE ARE IN A CLASS: State is saved from previous test !!!
        collection = conservator.collections.all().first()
        collection.remove_associated_file("lorem.txt")

        collection.populate("file_locker_files")
        # But now that it has files, it's not null it's an empty list.
        assert len(collection.file_locker_files) == 0
