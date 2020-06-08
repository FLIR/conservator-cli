import os

from FLIR.conservator_cli.lib.graphql_api import get_datasets_from_search
from FLIR.conservator_cli.lib.graphql_api import get_collection_by_path
from FLIR.conservator_cli.lib.graphql_api import get_dataset_by_id
from FLIR.conservator_cli.lib.graphql_api import get_history
from FLIR.conservator_cli.lib.graphql_api import get_videos_from_search, get_images_from_search, get_media_from_search
from FLIR.conservator_cli.lib.graphql_api import get_video_from_id, get_image_from_id, get_media_from_id
from FLIR.conservator_cli.lib.graphql_api import get_video_filelist, get_image_filelist, get_media_filelist
from FLIR.conservator_cli.lib.graphql_api import get_videos_by_collection_id, get_images_by_collection_id, get_media_by_collection_id
from FLIR.conservator_cli.lib.graphql_api import get_videos_from_collection, get_images_from_collection, get_media_from_collection

def get_datasets_from_search_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    assert len(datasets) > 0
    assert datasets[0]["id"]
    assert datasets[0]["name"]
    assert datasets[0]["repository"]
    assert datasets[0]["repository"]["master"]

def get_dataset_by_id_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    dataset = get_dataset_by_id(datasets[0]["id"], access_token)
    assert dataset["id"]
    assert dataset["name"]
    assert dataset["repository"]
    assert dataset["repository"]["master"]

def get_history_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    datasets = get_datasets_from_search("rodeo", access_token)
    history = get_history(datasets[0]["repository"]["master"], access_token)
    assert len(history) > 0

def get_collection_by_path_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    collection = get_collection_by_path("/integration-test", access_token)
    assert collection["id"] == "LwWYEXHEGKTCRCc8C"

def get_media_from_search_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    # look for a test video
    video_search = "filename:5_second_cut.mp4"
    video_id = "D3uDd2T3x7JTh6jb3"
    videos = get_videos_from_search(video_search, access_token)
    media = get_media_from_search(video_search, access_token)
    print("Videos:",videos)
    print("Media:",media)
    found_in_videos = video_id in [v["id"] for v in videos] 
    found_in_media = video_id in [m["id"] for m in media] 
    assert(found_in_videos)
    assert(found_in_media)
    # look for a test image
    image_search = "filename:20190921_105506_459_8b.JPG"
    image_id = "gDC359JXq5y7BRzpg"
    images = get_images_from_search(image_search, access_token)
    media = get_media_from_search(image_search, access_token)
    print("Images:",images)
    print("Media:",media)
    found_in_images = image_id in [i["id"] for i in images] 
    found_in_media = image_id in [m["id"] for m in media] 
    assert(found_in_images)
    assert(found_in_media)

def get_media_from_id_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    # look for a test video
    video_id = "D3uDd2T3x7JTh6jb3"
    video = get_video_from_id(video_id, access_token)
    media = get_media_from_id(video_id, access_token)
    print("Video:",video)
    print("Media:",media)
    found_in_videos = video and video["id"] == video_id
    found_in_media = media and media["id"] == video_id
    assert(found_in_videos)
    assert(found_in_media)
    # look for a test image
    image_id = "gDC359JXq5y7BRzpg"
    image = get_image_from_id(image_id, access_token)
    media = get_media_from_id(image_id, access_token)
    print("Image:",image)
    print("Media:",media)
    found_in_images = image and image["id"] == image_id
    found_in_media = media and media["id"] == image_id
    assert(found_in_images)
    assert(found_in_media)

def get_media_filelist_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    collection_id = "LwWYEXHEGKTCRCc8C"
    videos = get_video_filelist(collection_id, access_token)
    images = get_image_filelist(collection_id, access_token)
    media = get_media_filelist(collection_id, access_token)
    video_files = [v["filename"] for v in videos]
    image_files = [i["filename"] for i in images]
    media_files = [m["filename"] for m in media]
    print("Videos:",video_files)
    print("Images:",image_files)
    print("Media:",media_files)
    assert(video_files and image_files and media_files)
    assert((video_files + image_files).sort() == media_files.sort())

def get_media_by_collection_id_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    collection_id = "LwWYEXHEGKTCRCc8C"
    videos = get_videos_by_collection_id(collection_id, access_token)["videos"]
    images = get_images_by_collection_id(collection_id, access_token)["images"]
    media = get_media_by_collection_id(collection_id, access_token)["media"]
    video_files = [v["filename"] for v in videos]
    image_files = [i["filename"] for i in images]
    media_files = [m["filename"] for m in media]
    print("Videos:",video_files)
    print("Images:",image_files)
    print("Media:",media_files)
    assert(video_files and image_files and media_files)
    assert((video_files + image_files).sort() == media_files.sort())

def get_media_from_collection_test():
    access_token = os.environ["CONSERVATOR_TOKEN"]
    collection_id = "LwWYEXHEGKTCRCc8C"
    videos = get_videos_from_collection(collection_id, access_token)
    images = get_images_from_collection(collection_id, access_token)
    media = get_media_from_collection(collection_id, access_token)
    video_files = [v["filename"] for v in videos]
    image_files = [i["filename"] for i in images]
    media_files = [m["filename"] for m in media]
    print("Videos:",video_files)
    print("Images:",image_files)
    print("Media:",media_files)
    assert(video_files and image_files and media_files)
    assert((video_files + image_files).sort() == media_files.sort())
