

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
