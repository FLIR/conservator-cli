import os
import requests
import sys
import time

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated.schema import Mutation, Query
from FLIR.conservator.util import md5sum_file, chunks
from PIL import Image

conservator = Conservator.default()

md5_assets_fields = [
    "md5",
    "dataset_details.dataset_frame.id",
    "video_details.frame.id",
]


def upload_image_and_return_metadata(image_path, frame_index=0):
    image_md5 = md5sum_file(image_path)

    md5_assets = conservator.query(
        Query.assets_by_md5s, md5s=[image_md5], fields=md5_assets_fields
    )

    file_name = os.path.split(image_path)[1]

    asset = md5_assets[0]

    dataset_details_count = len(asset.dataset_details)

    video_details_count = len(asset.video_details)

    if dataset_details_count > 0 or video_details_count > 0:
        print(f"{file_name} already exists in Conservator; skipping upload")
    else:
        # If it doesn't, upload it
        tries = 5

        url = conservator.get_dvc_hash_url(image_md5)

        headers = {
            "Content-type": "image/jpeg",
            "x-amz-meta-originalfilename": file_name,
        }
        print(f"Uploading {image_path}.")
        retry_count = 0
        while retry_count < tries:
            with open(image_path, "rb") as data:
                r = requests.put(url, data, headers=headers)
            if r.status_code == 502:
                retry_count += 1
                if retry_count < tries:
                    print(f"Bad Gateway error, retrying {file_name} ..")
                    time.sleep(retry_count)  # Timeout increases per retry.
                    continue
            else:
                break
        assert r.status_code == 200
        assert r.headers["ETag"] == f'"{image_md5}"'

    # Add the frame to the dataset
    file_size = os.path.getsize(image_path)

    image = Image.open(image_path)

    new_frame = {
        "frameIndex": frame_index,
        "previewWidth": image.width,
        "previewHeight": image.height,
        "width": image.width,
        "height": image.height,
        "md5": image_md5,
        "fileSize": file_size,
        "previewMd5": image_md5,
        "previewFileSize": file_size,
    }

    return new_frame


if __name__ == "__main__":
    # First, read in dataset id and confirm it exists
    dataset_id = input("Please provide a dataset id: ")

    try:
        dataset = conservator.query(Query.dataset, id=dataset_id)
    except Exception as err:
        print(f"Error looking up dataset {dataset_id}")
        print(err)
        sys.exit(1)

    # Then, read in image path, and check if it exists in conservator
    image_dir = input(
        "Please enter the absolute path to a directory containing JPEGs: "
    )

    while not os.path.exists(image_dir):
        image_dir = input(
            "Please enter the absolute path to a directory containing JPEGs: "
        )

    file_extensions = ["JPG", "JPEG", "jpg", "jpeg"]

    image_names = [
        os.path.join(image_dir, file)
        for file in os.listdir(image_dir)
        if any(file.endswith(ext) for ext in file_extensions)
    ]

    image_names.sort()

    frame = upload_image_and_return_metadata(image_names[0], 0)

    image_chunks = chunks(image_names, 5)

    frame_index = 0

    for chunk in image_chunks:
        frames_to_create = []

        for image_path in chunk:
            if image_path is not None:
                frame = upload_image_and_return_metadata(image_path, frame_index)
                frames_to_create.append(frame)
                frame_index = frame_index + 1

        new_frames = conservator.query(
            Mutation.create_dataset_frames,
            dataset_id=dataset_id,
            dataset_frames=frames_to_create,
        )

    print(f"Created {len(image_names)} new frames in dataset {dataset.name}")
