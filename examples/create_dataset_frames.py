# pylint: disable=broad-except
import os
import sys
import time
import requests

from PIL import Image

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation, Query
from FLIR.conservator.util import md5sum_file, chunks

conservator = Conservator.default()


def upload_image_and_return_metadata(upload_image_path, image_frame_index=0):
    """
    This function takes an image path an optional frame index,
    and returns an object suitable to pass to the
    create_dataset_frames API
    """
    image_md5 = md5sum_file(upload_image_path)

    # This API call checks if the image's md5 exists in Conservator
    does_md5_exist = conservator.query(Query.does_md5_exist, md5=image_md5)

    file_name = os.path.split(upload_image_path)[1]

    if does_md5_exist:
        print(f"{file_name} already exists in Conservator; skipping upload")
    else:
        # If the image doesn't exist, upload it to Conservator.
        # This code is adapted from the upload_image function in
        # FLIR/conservator/cli/cvc.py
        tries = 5

        url = conservator.get_dvc_hash_url(image_md5)

        headers = {
            "Content-type": "image/jpeg",
            "x-amz-meta-originalfilename": file_name,
        }
        print(f"Uploading {upload_image_path}.")
        retry_count = 0
        while retry_count < tries:
            with open(upload_image_path, "rb") as data:
                response = requests.put(url, data, headers=headers, timeout=10)
            if response.status_code == 502:
                retry_count += 1
                if retry_count < tries:
                    print(f"Bad Gateway error, retrying {file_name} ..")
                    time.sleep(retry_count)  # Timeout increases per retry.
                    continue
            else:
                break
        assert response.status_code == 200
        assert response.headers["ETag"] == f'"{image_md5}"'

    # create_dataset_frames needs the image's file size
    file_size = os.path.getsize(upload_image_path)

    # create_dataset_frames also needs the image's dimensions
    image = Image.open(upload_image_path)

    # We're not creating a preview image, so the preview values
    # are the same as the actual values.
    # If desired, it would be possible to create and upload a preview
    # version of the image using Pillow; e.g.
    #
    # im = Image.open("/home/example/image.jpg")
    # im.thumbnail((640, 480), Image.ANTIALIAS)
    # im.save("/home/example/preview_image.jpg", "JPEG")
    new_frame = {
        "frameIndex": image_frame_index,
        "previewWidth": image.width,
        "width": image.width,
        "previewHeight": image.height,
        "height": image.height,
        "previewMd5": image_md5,
        "md5": image_md5,
        "previewFileSize": file_size,
        "fileSize": file_size,
    }

    return new_frame


if __name__ == "__main__":
    # First, read in dataset id and confirm it exists
    # For this example, just create a new dataset manually
    dataset_id = input("Please provide a dataset id: ")

    try:
        dataset = conservator.query(Query.dataset, id=dataset_id)
    except Exception as err:
        print(f"Error looking up dataset {dataset_id}")
        print(err)
        sys.exit(1)

    # Then, read in a directory, presumed to contain JPEG files
    image_dir = input(
        "Please enter the absolute path to a directory containing JPEGs: "
    )

    # Loop until user enters a path that exists...
    while not os.path.exists(image_dir):
        image_dir = input(
            "Please enter the absolute path to a directory containing JPEGs: "
        )

    # List of valid extensions
    file_extensions = ["JPG", "JPEG", "jpg", "jpeg"]

    # Get a list of JPEG files from the directory
    # We could validate further using Pillow;
    # the Image constructor will throw an exception if
    # the supplied file is not a valid image
    image_names = [
        os.path.join(image_dir, file)
        for file in os.listdir(image_dir)
        if any(file.endswith(ext) for ext in file_extensions)
    ]

    # Need to sort the images; typically we expect images
    # to have sequential numeric names, left padded with zeroes
    # e.g. '00001.jpg, 00002.jpg, ...00100.jpg'
    image_names.sort()

    # This function takea a list of objects and returns
    # an iterator of smaller lists (in this case, of length 5 each)
    image_chunks = chunks(image_names, 5)

    # Start frame indexing at the dataset frame count
    # (which defaults to 0)
    dataset.populate(["frame_count"])
    frame_index = dataset.frame_count

    for chunk in image_chunks:
        frames_to_create = []

        for image_path in chunk:
            # Check that the path isn't None; see comment on the
            # chunks function in FLIR/conservator/util.py
            if image_path is not None:
                # Upload image, if necessary, and add the returned
                # frame object to the list of frames to create
                frame = upload_image_and_return_metadata(image_path, frame_index)
                frames_to_create.append(frame)
                frame_index += 1

        # Create 5 frames; it should be possible to create more
        # than 5 at a time, depending on server load and other factors.
        # YMMV
        new_frames = conservator.query(
            Mutation.create_dataset_frames,
            dataset_id=dataset_id,
            dataset_frames=frames_to_create,
        )

    print(f"Created {len(image_names)} new frames in dataset {dataset.name}")
