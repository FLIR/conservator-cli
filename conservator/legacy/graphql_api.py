#!/usr/bin/env python3
import sys
import time

import requests

from pyconservator.legacy import terminal_progress_bar as tpb


class ConservatorGraphQLServerError(Exception):
    def __init__(self, status_code, message, server_error):
        self.status_code = status_code
        self.message = message
        self.server_error = server_error


# default time before next attempt to retry a failed graphql query
RETRY_DELAY = 1.0

# default number of retry attempts for a failed graphql query
MAX_RETRIES = 10


def query_conservator(query, variables, access_token, retry_delay=RETRY_DELAY, max_retries=MAX_RETRIES):
    graphql_endpoint = 'https://flirconservator.com/graphql'
    headers = {'authorization': "{}".format(access_token)}
    response = {}

    last_exception = None
    for attempt in range(0, max_retries):
        # request can fail with flaky network connections;
        # parsing can fail if server responds, but with an http error
        try:
            r = requests.post(graphql_endpoint, headers=headers, json={"query": query, "variables": variables})
            response = r.json()
            last_exception = None
            break
        # Bail out on signal exceptions.
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            # Capture exception to re-throw it later.
            last_exception = exc
            pass

        # something went wrong, wait before retrying
        time.sleep(retry_delay)

    if last_exception is not None:
        raise last_exception

    # response with 'data' but not 'errors' means valid results
    if response.get("errors"):
        raise ConservatorGraphQLServerError(r.status_code, "Server rejected query", r.content)
    elif response.get("data"):
        result = response["data"]
    else:
        raise ConservatorGraphQLServerError(r.status_code, "Invalid server response", r.content)
    return result


def get_user_data(access_token):
    graphql_endpoint = 'https://flirconservator.com/graphql'
    headers = {'authorization': "{}".format(access_token)}
    query = """
    {
      user {
        id
        email
      }
    }
    """
    r = requests.post(graphql_endpoint, headers=headers, json={"query": query})
    response = r.json()
    return response["data"]["user"]


def get_datasets_from_search(search_text, access_token):
    query = """
    query datasets($searchText: String!) {
      datasets(searchText: $searchText, page: 0, limit: 50) {
        name
        id
        repository {
            master
        }
      }
    }
    """
    variables = {
        "searchText": search_text
    }
    return query_conservator(query, variables, access_token)["datasets"]


def get_dataset_metadata(dataset_id, access_token):
    query = """
    mutation generateDatasetMetadata($datasetId: ID!) {
      generateDatasetMetadata(datasetId: $datasetId)
    }
    """
    variables = {
        "datasetId": dataset_id
    }
    data = query_conservator(query, variables, access_token)
    return data["generateDatasetMetadata"]


def get_dataset_frame(dataset_frame_id, access_token):
    query = """
    query datasetFrame($id: ID!, $searchText: String) {
      datasetFrame(id: $id, searchText: $searchText) {
        id
        frameId
        videoId
        frameIndex
      }
    }
    """
    variables = {
        "id": dataset_frame_id,
        "searchText": None
    }
    data = query_conservator(query, variables, access_token)
    return data["datasetFrame"]


def get_dataset_by_id(dataset_id, access_token):
    query = """
    query dataset($datasetId: ID!) {
      dataset(id: $datasetId) {
        name
        id
        repository {
            master
        }
      }
    }
    """
    variables = {
        "datasetId": dataset_id
    }
    return query_conservator(query, variables, access_token)["dataset"]


def get_history(commit_hash, access_token):
    query = """
    query commitHistoryById($hash: String!) {
      commitHistoryById(id: $hash) {
          _id
      }
    }
    """
    variables = {
        "hash": commit_hash
    }
    return query_conservator(query, variables, access_token)["commitHistoryById"]


#######################
## videos and images ##
#######################

##---------------------
## query on search text
##---------------------

# function generator with common code to be specialized for media type
def funcgen_get_x_from_search(media_type):
    def get_x_from_search(search_text, access_token):
        medias = media_type + "s"  # e.g. "videos" or "images"
        query = """
        query {medias}($searchText: String) {{
            {medias}(searchText: $searchText, limit: 100, page: 0) {{
            id
            filename
            url
            }}
        }}
        """.format(medias=medias)
        variables = {
            "searchText": search_text
        }
        return query_conservator(query, variables, access_token)[medias]

    return get_x_from_search


# generate query function for videos
get_videos_from_search = funcgen_get_x_from_search("video")

# generate query function for images
get_images_from_search = funcgen_get_x_from_search("image")


# query including both videos AND images
def get_media_from_search(search_text, access_token):
    videos = get_videos_from_search(search_text, access_token)
    images = get_images_from_search(search_text, access_token)
    return videos + images


##------------------
## query on filename
##------------------

# function generator with common code to be specialized for media type
def funcgen_get_x_from_filename(media_type):
    def get_x_from_filename(filename, collection_id, access_token):
        medias = media_type + "s"  # e.g. "videos" or "images"
        query = """
        query {medias}($searchText: String, $collectionId: ID!) {{
            {medias}(searchText: $searchText, collectionId: $collectionId, limit: 100, page: 0) {{
            id
            filename
            url
            }}
        }}
        """.format(medias=medias)
        variables = {
            "searchText": "filename:" + filename,
            "collectionId": collection_id
        }
        return query_conservator(query, variables, access_token)[medias]

    return get_x_from_filename


# generate query function for videos
get_videos_from_filename = funcgen_get_x_from_filename("video")

# generate query function for images
get_images_from_filename = funcgen_get_x_from_filename("image")


# query including both videos AND images
def get_media_from_filename(filename, collection_id, access_token):
    videos = get_videos_from_filename(filename, collection_id, access_token)
    images = get_images_from_filename(filename, collection_id, access_token)
    return videos + images


##------------
## query on id
##------------

# function generator with common code to be specialized for media type
def funcgen_get_x_from_id(media_type):
    def get_x_from_id(media_id, access_token):
        query = """
        query {media}($id: String!, $src: String) {{
          {media}(id: $id, src: $src) {{
            id
            filename
            url
            frames {{
                id
                url
                frameIndex
                annotations {{
                    id
                    labels
                    boundingBox {{
                        x
                        y
                        w
                        h
                    }}
                }}
            }}
          }}
        }}
        """.format(media=media_type)
        variables = {
            "id": media_id,
            "src": ""
        }
        return query_conservator(query, variables, access_token)[media_type]

    return get_x_from_id


# generate query function for videos
get_video_from_id = funcgen_get_x_from_id("video")

# generate query function for images
get_image_from_id = funcgen_get_x_from_id("image")


# query including both videos AND images
def get_media_from_id(media_id, access_token):
    result = get_video_from_id(media_id, access_token)
    if not result:
        result = get_image_from_id(media_id, access_token)
    return result


##----------------------------
## query media in a collection
##----------------------------

# WARNING: there is currently a Conservator bug where the non-recursive
#          counts can be too small, so don't trust them too much...
def get_media_counts(collection_id, access_token):
    query = """
    query mediaCountRecursive($id: ID!) {
        collection(id: $id) {
            recursiveVideoCount
            videoCount
            recursiveImageCount
            imageCount
        }
    }
    """
    variables = {
        "id": collection_id
    }
    return query_conservator(query, variables, access_token)["collection"]


# function generator with common code to be specialized for media type
# and list of media object fields to be returned
def funcgen_paged_query(media_type, query_list):
    def paged_query(collection_id, access_token):
        medias = media_type + "s"  # e.g. "videos" or "images"
        page_size = 200  # number of entries returned per query
        query_fields = "\n".join(query_list)  # fields of interest, e.g. "id" or "name"

        result = []
        page_result = []
        page_offset = 0
        while True:
            query = """
            query paged_query($id: ID!, $limit: Int, $page: Int) {{
                {medias}(collectionId: $id, limit: $limit, page: $page) {{
                {query_fields}
              }}
            }}
            """.format(medias=medias, query_fields=query_fields)
            variables = {
                "id": collection_id,
                "limit": page_size,
                "page": page_offset
            }
            page_result = query_conservator(query, variables, access_token)[medias]
            # keep going as long as there are new results
            if page_result:
                result += page_result
                page_offset += 1
            else:
                break
        return result

    return paged_query


##
## get_*_filelist: list files with url
##

# generate query function for videos
get_video_filelist = funcgen_paged_query("video", ["id", "filename", "url"])

# generate query function for images
get_image_filelist = funcgen_paged_query("image", ["id", "filename", "url"])


# query including both videos AND images
def get_media_filelist(collection_id, access_token):
    videos = get_video_filelist(collection_id, access_token)
    images = get_image_filelist(collection_id, access_token)
    return videos + images


##
## get_*_by_collection_id: list files with url and tags
##                         note result list is returned as field in a dict
##

# generate query function for videos
get_videos_by_collection_id_helper = funcgen_paged_query("video", ["id", "filename", "url", "tags"])


def get_videos_by_collection_id(collection_id, access_token):
    video_list = get_videos_by_collection_id_helper(collection_id, access_token)
    return {"videos": video_list}


# generate query function for images
get_images_by_collection_id_helper = funcgen_paged_query("image", ["id", "filename", "url", "tags"])


def get_images_by_collection_id(collection_id, access_token):
    image_list = get_images_by_collection_id_helper(collection_id, access_token)
    return {"images": image_list}


# query including both videos AND images
def get_media_by_collection_id(collection_id, access_token):
    videos = get_videos_by_collection_id(collection_id, access_token)
    images = get_images_by_collection_id(collection_id, access_token)
    # merge lists of "videos" and "images" and call it "media"
    media = {"media": videos["videos"] + images["images"]}
    return media


##
## get_*_from_collection: list files with url, tags, and number of frames
##

# generate query function for videos
get_videos_from_collection = funcgen_paged_query("video", ["id", "name", "filename", "url", "tags", "framesCount"])

# generate query function for images
get_images_from_collection = funcgen_paged_query("image", ["id", "name", "filename", "url", "tags", "framesCount"])


# query including both videos AND images
def get_media_from_collection(collection_id, access_token):
    videos = get_videos_from_collection(collection_id, access_token)
    images = get_images_from_collection(collection_id, access_token)
    return videos + images


##----------------------------

def download_file(filename, url, show_progress=True, tab_number=0):
    r = requests.get(url, stream=True)
    print("\t" * tab_number + "Downloading {} ({:.2f} MB) ...".format(filename,
                                                                      int(r.headers["content-length"]) / 1024 / 1024))
    total = 0
    chunk_size = 1024
    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            total += chunk_size
            if show_progress:
                tpb.printProgressBar(total, int(r.headers["content-length"]), "\t" * tab_number + "Download Progress:",
                                     "Complete", 1, 50)
            fd.write(chunk)
    if show_progress:
        print()


def get_collection_by_path(path, access_token):
    query = """
    query collectionByPath($path: String!) {
      collectionByPath(path: $path) {
          id
        name
        childIds
        fileLockerFiles {
            url
            name
        }
      }
    }
    """
    variables = {
        "path": path
    }
    return query_conservator(query, variables, access_token)["collectionByPath"]


def create_collection(name, parent_id, access_token):
    query = """
    mutation createCollection($input: CreateCollectionInput!) {
      createCollection(input: $input) {
          id
        name
        childIds
        fileLockerFiles {
            url
            name
        }
      }
    }
    """
    variables = {
        "input": {"name": name, "parentId": parent_id}
    }
    return query_conservator(query, variables, access_token)["createCollection"]


def get_collection_by_id(id, access_token):
    query = """
    query collection($id: ID!) {
      collection(id: $id) {
          id
        name
        childIds
        fileLockerFiles {
            url
            name
        }
      }
    }
    """
    variables = {
        "id": id
    }
    return query_conservator(query, variables, access_token)["collection"]


def get_datasets_from_collection(collection_id, access_token):
    query = """
    query getFirstNDatasets($id: ID!, $n: Int, $searchText: String) {
      getFirstNDatasets(id: $id, n: $n, searchText: $searchText) {
          id
        name
        tags
        frameCount
        repository {
            master
        }
      }
    }
    """
    variables = {
        "id": collection_id,
        "n": 200,
        "searchText": ""
    }
    return query_conservator(query, variables, access_token)["getFirstNDatasets"]


def create_video(filename, access_token):
    query = """
    mutation CreateVideo($filename: String!) {
      createVideo(filename: $filename) {
        id
      }
    }
    """
    variables = {
        "filename": filename
    }
    return query_conservator(query, variables, access_token)["createVideo"]


def get_frames_from_video(video_id, access_token):
    query = """
    query getFrames($video_id: String!) {
      video(id: $video_id) {
        frames {
            id
            frameIndex
        }
      }
    }
    """
    variables = {
        "video_id": video_id
    }
    return query_conservator(query, variables, access_token)["video"]


def get_video_metadata(id, access_token):
    query = """
    query video($id: String!) {
      video(id: $id) {
        metadata
      }
    }
    """
    variables = {
        "id": id
    }
    return query_conservator(query, variables, access_token)["video"]


def get_annotations(video_id, access_token):
    query = """
    query annotationsByVideoId($id: ID!) {
      annotationsByVideoId(id: $id) {
        id
        labels
        boundingBox {
            x
            y
            w
            h
        }
        source {
            type
            meta {
                tool
                classifierId
                originalId
                comment
            }
        }
      }
    }
    """
    variables = {
        "id": video_id
    }
    return query_conservator(query, variables, access_token)["annotationsByVideoId"]


def create_annotation(frame_id, label, bounding_box, access_token):
    query = """
    mutation createAnnotation($frameId: String!, $annotation: AnnotationCreate!) {
      createAnnotation(frameId: $frameId, annotation: $annotation) {
        id
        labels
        boundingBox {
            x
            y
            w
            h
        }
        source {
            type
            meta {
                tool
                classifierId
                originalId
                comment
            }
        }
      }
    }
    """
    variables = {
        "frameId": frame_id,
        "annotation": {
            "labels": [label],
            "boundingBox": {
                "x": bounding_box[0],
                "y": bounding_box[1],
                "w": bounding_box[2],
                "h": bounding_box[3]
            },
            "targetId": "n/a"
        }
    }
    return query_conservator(query, variables, access_token)["createAnnotation"]


def mark_annotation_as_uploaded(id, url, access_token):
    query = """
    mutation markAnnotationAsUploaded($id: String!, $url: String!) {
      markAnnotationAsUploaded(id: $id, url: $url)
    }
    """
    variables = {
        "id": id,
        "url": url
    }
    return query_conservator(query, variables, access_token)["markAnnotationAsUploaded"]


def get_signed_meta_upload_url(video_id, content_type, filename, access_token):
    query = """
    mutation generateSignedMetadataUploadUrl($videoId: String!, $contentType: String!, $filename: String!) {
      generateSignedMetadataUploadUrl(videoId: $videoId, contentType: $contentType, filename: $filename) {
          url
        signedUrl
      }
    }
    """
    variables = {
        "videoId": video_id,
        "contentType": content_type,
        "filename": filename
    }
    return query_conservator(query, variables, access_token)["generateSignedMetadataUploadUrl"]


def get_signed_upload_url(video_id, content_type, access_token):
    query = """
    mutation GenerateSignedVideoUploadUrl($videoId: String!, $contentType: String!) {
      generateSignedVideoUploadUrl(videoId: $videoId, contentType: $contentType) {
        signedUrl
      }
    }
    """
    variables = {
        "videoId": video_id,
        "contentType": content_type
    }
    return query_conservator(query, variables, access_token)["generateSignedVideoUploadUrl"]


def get_signed_video_locker_upload_url(video_id, content_type, filename, access_token):
    query = """
    mutation generateSignedFileLockerUploadUrl($videoId: String!, $contentType: String!, $filename: String!) {
      generateSignedFileLockerUploadUrl(videoId: $videoId, contentType: $contentType, filename: $filename) {
        signedUrl
      }
    }
    """
    variables = {
        "videoId": video_id,
        "contentType": content_type,
        "filename": filename
    }
    return query_conservator(query, variables, access_token)["generateSignedFileLockerUploadUrl"]


def get_signed_dataset_locker_url(dataset_id, content_type, filename, access_token):
    query = """
    mutation generateSignedDatasetFileLockerUploadUrl($datasetId: ID!, $contentType: String!, $filename: String!) {
      generateSignedDatasetFileLockerUploadUrl(datasetId: $datasetId, contentType: $contentType, filename: $filename) {
        signedUrl
      }
    }
    """
    variables = {
        "datasetId": dataset_id,
        "contentType": content_type,
        "filename": filename
    }
    return query_conservator(query, variables, access_token)["generateSignedDatasetFileLockerUploadUrl"]


def get_signed_collection_locker_url(collection_id, content_type, filename, access_token):
    query = """
    mutation generateSignedCollectionFileLockerUploadUrl($collectionId: ID!, $contentType: String!, $filename: String!) {
      generateSignedCollectionFileLockerUploadUrl(collectionId: $collectionId, contentType: $contentType, filename: $filename) {
        signedUrl
      }
    }
    """
    variables = {
        "collectionId": collection_id,
        "contentType": content_type,
        "filename": filename
    }
    return query_conservator(query, variables, access_token)["generateSignedCollectionFileLockerUploadUrl"]


def upload_video_to_s3(filename, s3_url, content_type, show_progress=True):
    print("Uploading {} ...".format(filename))
    data = tpb.ProgressFileWrapper(filename, "rb") if show_progress else open(filename, "rb")
    requests.put(s3_url, data, headers={"Content-Type": content_type})
    if show_progress:
        print()


def delete_video(id, access_token):
    query = """
    mutation removeVideo($id: String!) {
      removeVideo(id: $id)
    }
    """
    variables = {
        "id": id
    }
    return query_conservator(query, variables, access_token)["removeVideo"]


def trigger_video_processing(id, metadata_url, should_notify, access_token):
    query = """
    mutation ProcessVideo($id: String!, $metadataUrl: String, $shouldNotify: Boolean) {
          processVideo(id: $id, metadataUrl: $metadataUrl, shouldNotify: $shouldNotify) {
            id
          }
    }
    """
    variables = {
        "id": id,
        "metadataUrl": metadata_url,
        "shouldNotify": should_notify
    }
    return query_conservator(query, variables, access_token)["processVideo"]


def add_frames_to_dataset(dataset_id, frame_ids, access_token):
    query = """
    mutation addFramesToDataset($input: AddFramesToDatasetInput!) {
          addFramesToDataset(input: $input) {
            id
          }
    }
    """
    variables = {
        "input": {
            "datasetId": dataset_id,
            "frameIds": frame_ids
        }
    }
    result = query_conservator(query, variables, access_token)
    return result["addFramesToDataset"]


class InvalidRepoName(Exception):
    pass


class Repo:
    def __init__(self, name, conservator_token):
        self.name = name
        self.conservator_token = conservator_token
        data = get_datasets_from_search(self.name, self.conservator_token)
        if (data['datasets'] == None):
            raise InvalidRepoName("Could not find repo '{}' in Conservator".format(self.name))
        for dataset in data['datasets']:
            if (dataset["name"] == self.name):
                self.dataset_id = dataset["id"]
        if (self.dataset_id == None):
            raise InvalidRepoName("Could not find repo '{}' in Conservator".format(self.name))

    def get_latest_commit(self):
        data = get_repository(self.dataset_id, self.conservator_token)
        return data["dataset"]["repository"]["master"]

    def get_dataset_id(self):
        return self.dataset_id


if __name__ == "__main__":
    main(sys.argv)
