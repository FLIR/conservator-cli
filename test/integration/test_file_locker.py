import os
import pytest as pytest

from FLIR.conservator.util import md5sum_file
from conftest import upload_media


class TestFileLockerImage:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        upload_media(conservator, MEDIA)

    def test_file_locker_files_start_null(self, conservator):
        image = conservator.images.all().first()
        image.populate("file_locker_files")
        # For some reason, it starts as null
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

