#!/usr/bin/env python3
import requests
import sys

from FLIR.common.lib import terminal_progress_bar as tpb


class ConservatorGraphQLServerError(Exception):
	def __init__(self, status_code, message, server_error):
		self.status_code = status_code
		self.message = message
		self.server_error = server_error


def query_conservator(query, variables, access_token):
	graphql_endpoint = 'https://flirconservator.com/graphql'
	headers = {'authorization': "{}".format(access_token) }
	r = requests.post(graphql_endpoint, headers=headers, json={"query":query, "variables":variables})
	try:
		response = r.json()
	except:
		raise ConservatorGraphQLServerError(
			r.status_code, "Invalid server response", r.content)
	if r.status_code not in (200, 201):
		server_message = ""
		if "errors" in response:
			server_message = response['errors']
		raise ConservatorGraphQLServerError(
			r.status_code, "Unexpected status code: {}, server message: {}".format(
				r.status_code, server_message), server_message)
	return response["data"]


def get_user_data(access_token):
	graphql_endpoint = 'https://flirconservator.com/graphql'
	headers = {'authorization': "{}".format(access_token) }
	query = """
	{
	  user {
	    id
	    email
	  }
	}
	"""
	r = requests.post(graphql_endpoint, headers=headers, json={"query":query})
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

def get_videos_from_search(search_text, access_token):
	query = """
	query videos($searchText: String) {
	  videos(searchText: $searchText, collectionId: 0, limit: 100, page: 0) {
		id
		filename
		url
	  }
	}
	"""
	variables = {
		"searchText": search_text
	}
	return query_conservator(query, variables, access_token)["videos"]

def get_videos_from_id(video_id, access_token):
	query = """
	query video($id: String!, $src: String) {
	  video(id: $id, src: $src) {
		id
		filename
		url
		frames {
			id
			url
			frameIndex
			annotations {
				id
				labels
				boundingBox {
					x
					y
					w
					h
				}
			}
		}
	  }
	}
	"""
	variables = {
		"id": video_id,
		"src": ""
	}
	return query_conservator(query, variables, access_token)["video"]

def get_media_counts(collection_id, access_token):
	query = """
	query imageCountRecursive($id: ID!) {
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


def get_video_filelist(collection_id, access_token):
	page_size = 200   # number of entries returned per query 
	vid_count = get_media_counts(collection_id, access_token)["videoCount"]
	num_pages = vid_count // page_size
	if vid_count % page_size:
		# one more if there is a partial page at end
		num_pages += 1

	result = []
	for page_offset in range(0, num_pages):
		query = """
		query video_filenames($id: ID!, $limit: Int, $page: Int) {
			videos(collectionId: $id, limit: $limit, page: $page) {
			filename
			url
		  }
		}
		"""
		variables = {
			"id": collection_id,
			"limit": page_size,
			"page": page_offset
		}
		result += query_conservator(query, variables, access_token)["videos"]
	return result

def get_image_filelist(collection_id, access_token):
	page_size = 200   # number of entries returned per query 
	img_count = get_media_counts(collection_id, access_token)["imageCount"]
	num_pages = img_count // page_size
	if img_count % page_size:
		# one more if there is a partial page at end
		num_pages += 1

	result = []
	for page_offset in range(0, num_pages):
		query = """
		query image_filenames($id: ID!, $limit: Int, $page: Int) {
			images(collectionId: $id, limit: $limit, page: $page) {
			filename
			url
		  }
		}
		"""
		variables = {
			"id": collection_id,
			"limit": page_size,
			"page": page_offset
		}
		result += query_conservator(query, variables, access_token)["images"]
	return result

def download_file(filename, url, show_progress=True, tab_number=0):
	r = requests.get(url, stream=True)
	print("\t"*tab_number + "Downloading {} ({:.2f} MB) ...".format(filename, int(r.headers["content-length"])/1024/1024))
	total = 0
	chunk_size = 1024
	with open(filename, 'wb') as fd:
		for chunk in r.iter_content(chunk_size=chunk_size):
			total += chunk_size
			if show_progress:
				tpb.printProgressBar(total, int(r.headers["content-length"]), "\t"*tab_number + "Download Progress:", "Complete", 1, 50)
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

def get_videos_by_collection_id(collection_id, access_token):
	query = """
	query videos($collectionId: ID!) {
		videos(collectionId: $collectionId, limit:100000) {
			id 
			filename
			url
			tags
		} 
	}
	"""
	variables = {
		"collectionId": collection_id
	}
	return query_conservator(query, variables, access_token)

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
		"n":200,
		"searchText":""
	}
	return query_conservator(query, variables, access_token)["getFirstNDatasets"]

def get_videos_from_collection(collection_id, access_token):
	query = """
	query getFirstNVideos($id: ID!, $n: Int, $searchText: String) {
	  getFirstNVideos(id: $id, n: $n, searchText: $searchText) {
	  	id
		name
		filename
		url
		tags
		framesCount
	  }
	}
	"""
	variables = {
		"id": collection_id,
		"n":1000,
		"searchText":""
	}
	return query_conservator(query, variables, access_token)["getFirstNVideos"]

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
				"x":bounding_box[0],
				"y":bounding_box[1],
				"w":bounding_box[2],
				"h":bounding_box[3]
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

def get_signed_video_locker_upload_url(video_id, content_type,filename, access_token):
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
        if(data['datasets'] == None):
            raise InvalidRepoName("Could not find repo '{}' in Conservator".format(self.name))
        for dataset in data['datasets']:
            if(dataset["name"] == self.name):
                self.dataset_id = dataset["id"]
        if(self.dataset_id == None):
            raise InvalidRepoName("Could not find repo '{}' in Conservator".format(self.name))

    def get_latest_commit(self):
        data = get_repository(self.dataset_id, self.conservator_token)
        return data["dataset"]["repository"]["master"]

    def get_dataset_id(self):
        return self.dataset_id

if __name__ == "__main__":
    main(sys.argv)
