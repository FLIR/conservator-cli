from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import Query, Mutation
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.wrappers.frame import Frame
from FLIR.conservator.wrappers.media import MediaType


class Video(MediaType):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos

    def get_annotations(self, fields=None):
        """
        Returns the video's annotations with the specified `fields`.
        """
        return self._conservator.query(
            Query.annotations_by_video_id, fields=fields, id=self.id
        )

    def trigger_processing(
        self,
        metadata_url=None,
        should_notify=False,
        should_object_detect=True,
        fields=None,
    ):
        """
        Trigger processing on a recently uploaded video.
        """
        return self._conservator.query(
            Mutation.process_video,
            operation_base=Mutation,
            fields=fields,
            id=self.id,
            metadata_url=metadata_url,
            should_notify=should_notify,
            should_object_detect=should_object_detect,
        )

    def remove(self):
        """
        Remove a video from conservator. Note that this is a permanent action that will
        remove it from **all** collections.
        """
        return self._conservator.query(
            Mutation.remove_video, operation_base=Mutation, id=self.id
        )

    def generate_signed_metadata_upload_url(self, filename, content_type):
        """
        Returns a signed url for uploading metadata with the given `filename` and
        `content_type`.
        """
        result = self._conservator.query(
            Mutation.generate_signed_metadata_upload_url,
            operation_base=Mutation,
            video_id=self.id,
            content_type=content_type,
            filename=filename,
        )
        return result.signed_url

    def generate_signed_upload_url(self, upload_id, part_number=1):
        """
        Returns a signed url for uploading a video (or part of video).

        :param upload_id: An upload id returned by :func:`initiate_upload`.
        :param part_number: The part number if uploading a multipart video.
        """
        result = self._conservator.query(
            Mutation.generate_signed_multipart_video_upload_url,
            operation_base=Mutation,
            part_number=part_number,
            upload_id=upload_id,
            video_id=self.id,
        )
        return result

    def generate_signed_locker_upload_url(self, filename, content_type):
        """
        Returns a signed url for uploading a new file locker file with the given `filename` and
        `content_type`.
        """
        result = self._conservator.query(
            Mutation.generate_signed_file_locker_upload_url,
            operation_base=Mutation,
            video_id=self.id,
            content_type=content_type,
            filename=filename,
        )
        return result.signed_url

    @staticmethod
    def create(conservator, filename, collection_id=None, fields=None):
        """
        Create a new video with the given `filename`. The video is added to
        under the collection with the given `collection_id` if specified,
        otherwise it is added to no collection (orphan video).

        The video is returned with the specified `fields`.
        """
        result = conservator.query(
            Mutation.create_video,
            operation_base=Mutation,
            fields=fields,
            filename=filename,
            collection_id=collection_id,
        )
        return Video(conservator, result)

    def initiate_upload(self, filename):
        """
        Initiate an upload to conservator with a remote `filename`,
        returning a new `upload_id`.
        """
        upload_id = self._conservator.query(
            Mutation.initiate_video_upload,
            operation_base=Mutation,
            video_id=self.id,
            filename=filename,
        )
        return upload_id

    def complete_upload(self, filename, upload_id, completion_tags=None):
        """
        Complete an upload to conservator, after having uploaded the video to
        the url given by :func:`generate_signed_upload_url`.

        :param filename: The name of the video.
        :param upload_id: An upload id returned by :func:`initiate_upload`.
        :param completion_tags: An optional list of completion tags, typically the ``ETag``
            headers from any S3 uploads.
        """
        if completion_tags is None:
            completion_tags = []
        result = self._conservator.query(
            Mutation.complete_video_upload,
            operation_base=Mutation,
            video_id=self.id,
            filename=filename,
            upload_id=upload_id,
            completion_tags=completion_tags,
        )
        assert result is True

    def get_frame_by_index(self, index, fields=None):
        """
        Returns a single frame at a specific `index` in the video.
        """
        return self._query_frames(frame_index=index, fields=fields)[0]

    def get_paginated_frames(self, start_index=0, fields=None):
        """
        Returns 15 frames, starting with `start_index`.

        This is only useful if you're dealing with very long videos
        and want to paginate frames yourself. If the video is short,
        you could just use ``populate("frames")`` to get all frames.
        """
        return self._query_frames(start_frame_index=start_index, fields=fields)

    def _query_frames(self, start_frame_index=None, frame_index=None, fields=None):
        fields = FieldsRequest.create(fields)

        video_fields = {
            "frames": {
                "start_frame_index": start_frame_index,
                "frame_index": frame_index,
            }
        }
        for path, value in fields.paths.items():
            new_path = "frames." + path
            video_fields[new_path] = value

        video = self._conservator.query(
            query=self.by_id_query,
            fields=video_fields,
            id=self.id,
        )
        return video.frames
