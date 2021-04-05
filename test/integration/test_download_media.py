import os

import pytest

from FLIR.conservator.util import md5sum_file
from conftest import upload_media


class TestDownloadMedia:
    """
    Using a class means that the same conservator instance will be reused for every test within.
    Tests are executed in order of declaration. Any pytest fixtures with `autouse` will be executed
    once before the tests.
    """

    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        MEDIA = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        upload_media(conservator, MEDIA)

    def test_download(self, conservator, tmp_cwd):
        image = conservator.images.by_exact_name("My cat.jpg").first()
        image.download(".")
        assert os.path.exists("My cat.jpg")
        assert os.path.isfile("My cat.jpg")
        assert md5sum_file("My cat.jpg") == image.md5

    def test_download_path(self, conservator, tmp_cwd):
        image = conservator.images.by_exact_name("My cat.jpg").first()
        image.download("Some/Path")
        assert os.path.exists("Some/Path/My cat.jpg")
        assert os.path.isfile("Some/Path/My cat.jpg")
        assert md5sum_file("Some/Path/My cat.jpg") == image.md5
