import json
import os

from FLIR.conservator.generated import schema
from FLIR.conservator.generated.schema import Query, Mutation
from FLIR.conservator.types.type_proxy import TypeProxy, requires_fields
from FLIR.conservator.util import download_file, upload_file


class Video(TypeProxy):
    underlying_type = schema.Video
    by_id_query = schema.Query.video
    search_query = schema.Query.videos

    @requires_fields("metadata", "filename")
    def download_metadata(self, path):
        json_data = json.loads(self.metadata)
        json_file = ".".join(self.filename.split(".")[:-1]) + ".json"
        json_path = os.path.join(path, json_file)
        with open(json_path, "w") as file:
            json.dump(json_data, file, indent=4, separators=(',', ': '))

    @requires_fields("url", "filename")
    def download(self, path):
        """Download video to ``path``."""
        download_file(path, self.filename, self.url)

    def get_annotations(self, fields=None):
        return self._conservator.query(Query.annotations_by_video_id,
                                       fields=fields, id=self.id)

    def get_frames(self, index, start_index, fields=None):
        return self._conservator.query(schema.Video.frames, operation_base=schema.Video,
                                       fields=fields, id=self.id,
                                       frame_index=index, start_frame_index=start_index)

    def trigger_processing(self, metadata_url=None, should_notify=False, should_object_detect=True, fields=None):
        return self._conservator.query(Mutation.process_video, operation_base=Mutation,
                                       fields=fields, id=self.id,
                                       metadata_url=metadata_url, should_notify=should_notify,
                                       should_object_detect=should_object_detect)

    def remove(self):
        return self._conservator.query(Mutation.remove_video, operation_base=Mutation,
                                       id=self.id)

    def generate_signed_metadata_upload_url(self, filename, content_type):
        result = self._conservator.query(Mutation.generate_signed_metadata_upload_url,
                                         operation_base=Mutation,
                                         video_id=self.id, content_type=content_type,
                                         filename=filename
                                         )
        return result.signed_url

    def generate_signed_upload_url(self, upload_id, part_number=1):
        result = self._conservator.query(Mutation.generate_signed_multipart_video_upload_url,
                                         operation_base=Mutation, part_number=part_number,
                                         upload_id=upload_id, video_id=self.id)
        return result

    def generate_signed_locker_upload_url(self, filename, content_type):
        result = self._conservator.query(Mutation.generate_signed_file_locker_upload_url,
                                         operation_base=Mutation,
                                         video_id=self.id, content_type=content_type,
                                         filename=filename)
        return result.signed_url

    @staticmethod
    def create(conservator, filename, collection_id=None, fields=None):
        result = conservator.query(Mutation.create_video, operation_base=Mutation,
                                   fields=fields,
                                   filename=filename, collection_id=collection_id)
        return Video(conservator, result)

    def initiate_upload(self, filename):
        upload_id = self._conservator.query(Mutation.initiate_video_upload, operation_base=Mutation,
                                            video_id=self.id, filename=filename)
        return upload_id

    def complete_upload(self, filename, upload_id, completion_tags=None):
        if completion_tags is None:
            completion_tags = []
        result = self._conservator.query(Mutation.complete_video_upload, operation_base=Mutation,
                                         video_id=self.id, filename=filename,
                                         upload_id=upload_id, completion_tags=completion_tags)
        assert result is True
