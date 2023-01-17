# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
import os

import pytest

from conftest import upload_media
from FLIR.conservator.conservator import UnknownMediaIdException
from FLIR.conservator.generated.schema import AnnotationCreate
from FLIR.conservator.util import md5sum_file
from FLIR.conservator.wrappers import Image, Video
from FLIR.conservator.wrappers.media import MediaCompare


def test_upload_image(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)

    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)

    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert image.id == media_id
    assert image.name == "cat_0.jpg"
    assert image.frame_count == 1


def test_upload_image_collection(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection)

    conservator.media.wait_for_processing(media_id)

    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert image.id == media_id
    assert image.name == "cat_0.jpg"
    assert image.frame_count == 1

    images = list(collection.get_images())
    assert len(images) == 1
    assert images[0].id == image.id


def test_upload_image_filename(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, remote_name="My cat photo")

    conservator.media.wait_for_processing(media_id)

    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert image.id == media_id
    assert image.name == "My cat photo"
    assert image.frame_count == 1


def test_upload_video(conservator, test_data):
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path)

    conservator.media.wait_for_processing(media_id)

    video = conservator.get_media_instance_from_id(media_id)
    assert video is not None
    assert video.id == media_id
    assert video.name == "adas_thermal.mp4"
    assert video.frame_count == 60


def test_upload_many_in_parallel(conservator, test_data):
    num_copies = 10
    path = test_data / "jpg" / "peds_0.jpg"
    new_filenames = [f"upload_many_test_{i}" for i in range(num_copies)]
    upload_tuples = [(path, filename) for filename in new_filenames]
    collection = conservator.collections.create_from_remote_path("/Many/Videos")

    media_ids = conservator.videos.upload_many_to_collection(
        upload_tuples, collection=collection, process_count=10
    )
    assert len(media_ids) == num_copies

    conservator.videos.wait_for_processing(media_ids)

    uploaded_filenames = []
    for media_id in media_ids:
        media = conservator.get_media_instance_from_id(media_id, fields="name")
        assert media is not None
        uploaded_filenames.append(media.name)
    # check that all submitted filenames came back as uploaded
    assert new_filenames.sort() == uploaded_filenames.sort()


def test_remove_image(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert isinstance(image, Image)

    image.remove()

    with pytest.raises(UnknownMediaIdException):
        conservator.get_media_instance_from_id(image.id)


def test_remove_video(conservator, test_data):
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    video = conservator.get_media_instance_from_id(media_id)
    assert video is not None
    assert isinstance(video, Video)

    video.remove()

    with pytest.raises(UnknownMediaIdException):
        conservator.get_media_instance_from_id(video.id)


def test_get_frame_by_index(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert isinstance(image, Image)

    frame_0 = image.get_frame_by_index(0)
    assert frame_0 is not None
    assert frame_0.video_id == image.id
    assert frame_0.video_name == image.name
    assert frame_0.height == 375
    assert frame_0.width == 500

    with pytest.raises(IndexError):
        image.get_frame_by_index(-1)

    with pytest.raises(IndexError):
        image.get_frame_by_index(1)


def test_image_get_frame(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert isinstance(image, Image)

    frame = image.get_frame()
    assert frame is not None
    assert frame.video_id == image.id
    assert frame.video_name == image.name
    assert frame.height == image.height
    assert frame.width == image.width


def test_get_all_frames_paginated(conservator, test_data):
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    video = conservator.get_media_instance_from_id(media_id)
    assert video is not None
    assert isinstance(video, Video)

    paginated_frames = video.get_all_frames_paginated()
    frames = list(paginated_frames)
    assert len(frames) == video.frame_count
    for i, frame in enumerate(frames):
        assert frame.frame_index == i
        assert frame.video_id == video.id
        assert frame.video_name == video.name
        assert frame.width == video.width
        assert frame.height == video.height


def test_compare_media(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.get_media_instance_from_id(media_id)

    assert image.compare(path) == MediaCompare.MATCH
    assert image.compare(path).ok()

    wrong_path = test_data / "jpg" / "cat_1.jpg"
    assert image.compare(wrong_path) == MediaCompare.MISMATCH
    assert not image.compare(wrong_path).ok()


def test_get_annotations_empty(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.get_media_instance_from_id(media_id)

    annotations = image.get_annotations()
    assert len(annotations) == 0


def test_get_annotations(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)
    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)
    image = conservator.images.all().first()

    frame = image.get_frame()
    annotation = AnnotationCreate(
        labels=["cat"], bounding_box={"x": 1, "y": 2, "w": 3, "h": 4}
    )
    added = frame.add_annotations([annotation])

    annotations = image.get_annotations()
    assert len(annotations) == 1
    assert annotations.to_json() == added.to_json()


def test_from_path(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection)
    conservator.media.wait_for_processing(media_id)

    image = conservator.media.from_path("/My/CatPics/cat_0.jpg")
    assert image is not None
    assert image.id == media_id


def test_from_string_image_path(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection)
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.from_string("/My/CatPics/cat_0.jpg")
    assert image is not None
    assert image.id == media_id


def test_from_string_image_id(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection)
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.from_string(media_id)
    assert image is not None
    assert image.id == media_id


def test_from_string_image_name(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection, remote_name="unique.jpg")
    conservator.media.wait_for_processing(media_id)

    image = conservator.images.from_string("unique.jpg")
    assert image is not None
    assert image.id == media_id


def test_from_string_video_path(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/Videos")
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path, collection)
    conservator.media.wait_for_processing(media_id)

    video = conservator.videos.from_string("/My/Videos/adas_thermal.mp4")
    assert video is not None
    assert video.id == media_id


def test_from_string_video_id(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/Videos")
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path, collection)
    conservator.media.wait_for_processing(media_id)

    video = conservator.videos.from_string(media_id)
    assert video is not None
    assert video.id == media_id


def test_from_string_video_name(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/Videos")
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path, collection, remote_name="unique.mp4")
    conservator.media.wait_for_processing(media_id)

    video = conservator.videos.from_string("unique.mp4")
    assert video is not None
    assert video.id == media_id


class TestDownloadMedia:
    @pytest.fixture(scope="class", autouse=True)
    def init_media(self, conservator, test_data):
        media_paths = [
            # local_path, remote_path, remote_name
            (test_data / "jpg" / "cat_2.jpg", "/Cats", "My cat.jpg"),
        ]
        upload_media(conservator, media_paths)

    @pytest.mark.usefixtures("tmp_cwd")
    def test_download(self, conservator):
        image = conservator.images.by_exact_name("My cat.jpg").first()
        image.download(".")
        assert os.path.exists("My cat.jpg")
        assert os.path.isfile("My cat.jpg")
        assert md5sum_file("My cat.jpg") == image.md5

    @pytest.mark.usefixtures("tmp_cwd")
    def test_download_path(self, conservator):
        image = conservator.images.by_exact_name("My cat.jpg").first()
        image.download("Some/Path")
        assert os.path.exists("Some/Path/My cat.jpg")
        assert os.path.isfile("Some/Path/My cat.jpg")
        assert md5sum_file("Some/Path/My cat.jpg") == image.md5
