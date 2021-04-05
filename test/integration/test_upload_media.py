def test_upload_image(conservator, test_data):
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path)

    conservator.media.wait_for_processing(media_id, check_frequency_seconds=1)

    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert image.id == media_id
    assert image.name == "cat_0.jpg"
    assert image.frames_count == 1


def test_upload_image_collection(conservator, test_data):
    collection = conservator.collections.create_from_remote_path("/My/CatPics")
    path = test_data / "jpg" / "cat_0.jpg"
    media_id = conservator.media.upload(path, collection)

    conservator.media.wait_for_processing(media_id)

    image = conservator.get_media_instance_from_id(media_id)
    assert image is not None
    assert image.id == media_id
    assert image.name == "cat_0.jpg"
    assert image.frames_count == 1

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
    assert image.frames_count == 1


def test_upload_video(conservator, test_data):
    path = test_data / "mp4" / "adas_thermal.mp4"
    media_id = conservator.media.upload(path)

    conservator.media.wait_for_processing(media_id)

    video = conservator.get_media_instance_from_id(media_id)
    assert video is not None
    assert video.id == media_id
    assert video.name == "adas_thermal.mp4"
    assert video.frames_count == 60
