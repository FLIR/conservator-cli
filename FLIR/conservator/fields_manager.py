import sgqlc.types
from FLIR.conservator.generated import schema


class FieldsManager:
    """
    Defines default fields for each SGQLC type.
    """

    @classmethod
    def select_default_fields(cls, selector):
        """
        Adds the default fields to the selector based on its type.

        For basic types with only scalars, all fields are included.
        For more complicated types, "useful" scalars are retained,
        with a few exceptions. In general, you should request only the
        specific fields you need. The fields included here may change
        at any time.

        See source for which fields are included.
        """
        # TODO: This behemoth of a method might be wise to split up...

        type_ = selector.__field__.type
        # by default, include everything.
        # later calls to specific fields will reduce the scope
        selector()

        if issubclass(type_, sgqlc.types.Scalar):
            return
        elif issubclass(type_, sgqlc.types.Enum):
            return
        elif issubclass(type_, schema.Acl):
            FieldsManager.select_default_fields(selector.read.user_ids)
            FieldsManager.select_default_fields(selector.read.group_ids)
            FieldsManager.select_default_fields(selector.write.user_ids)
            FieldsManager.select_default_fields(selector.write.group_ids)
            FieldsManager.select_default_fields(selector.admin.user_ids)
            FieldsManager.select_default_fields(selector.admin.group_ids)
        elif issubclass(type_, schema.Collection):
            selector.id()
            selector.parent_id()
            selector.project_id()
            selector.name()
            selector.video_count()
            selector.recursive_video_count()
            selector.dataset_count()
            selector.recursive_dataset_count()
            selector.image_count()
            selector.recursive_image_count()
            selector.child_count()
            selector.recursive_child_count()
            selector.path()
            selector.description()
        elif issubclass(type_, schema.Dataset):
            selector.id()
            selector.name()
            selector.frame_count()
            selector.video_count()
            selector.notes()
            selector.tags()
            selector.annotations_human_count()
            selector.annotations_machine_count()
            selector.readme()
            selector.annotated_frames()
            selector.empty_frames()
            selector.un_annotated_frames()
            selector.qa_change_requested_frames()
            selector.qa_approved_frames()
            selector.qa_pending_frames()
            selector.flagged_frames()
            selector.prediction_label_data()
            selector.annotation_label_data()
        elif issubclass(type_, schema.DatasetFrame):
            selector.id()
            selector.frame_id()
            selector.video_id()
            selector.frame_index()
            selector.url()
            selector.height()
            selector.width()
            selector.is_flagged()
            selector.is_empty()
            selector.annotation_count()
            selector.human_annotation_count()
            selector.machine_annotation_count()
            selector.qa_status()
            selector.md5()
            selector.description()
            selector.dataset_frame_name()
            selector.location()
            selector.spectrum()
        elif issubclass(type_, schema.DatasetFrames):
            FieldsManager.select_default_fields(selector.dataset_frames)
            selector.total_count()
        elif issubclass(type_, schema.Frame):
            selector.id()
            selector.video_id()
            selector.video_name()
            selector.url()
            selector.height()
            selector.width()
            selector.frame_index()
            selector.annotations_count()
            selector.machine_annotations_count()
            selector.qa_status()
            selector.description()
            selector.tags()
            selector.spectrum()
            selector.location()
            selector.prediction_label_data()
            selector.annotation_label_data()
            selector.md5()
            selector.is_flagged()
        elif issubclass(type_, schema.Frames):
            FieldsManager.select_default_fields(selector.frames)
            selector.total_count()
        elif issubclass(type_, schema.Group):
            selector.id()
            selector.name()
        elif issubclass(type_, schema.Image):
            selector.id()
            selector.filename()
            selector.url()
            selector.md5()
            selector.state()
            selector.frames_count()
            selector.annotations_count()
            selector.human_annotations_count()
            selector.name()
            selector.description()
            selector.location()
            selector.width()
            selector.height()
            selector.tags()
            selector.file_size()
            selector.spectrum()
            selector.image_md5()
        elif issubclass(type_, schema.LabelSet):
            selector.id()
            selector.name()
            selector.labels()
        elif issubclass(type_, schema.PaginatedFrames):
            FieldsManager.select_default_fields(selector.frames)
            selector.count()
        elif issubclass(type_, schema.Project):
            selector.id()
            selector.name()
            FieldsManager.select_default_fields(selector.root_collection)
            selector.description()
        elif issubclass(type_, schema.User):
            selector.id()
            selector.email()
            selector.name()
            selector.role()
            FieldsManager.select_default_fields(selector.groups)
            selector.is_removed()
        elif issubclass(type_, schema.Repository):
            selector.master()
            selector.repo_state()
        elif issubclass(type_, schema.Video):
            selector.id()
            selector.filename()
            selector.url()
            selector.md5()
            selector.state()
            selector.frame_count()
            selector.annotations_count()
            selector.human_annotations_count()
            selector.name()
            selector.description()
            selector.location()
            selector.width()
            selector.height()
            selector.tags()
            selector.frame_rate()
            selector.duration()
            selector.prediction_label_data()
            selector.annotation_label_data()
            selector.file_size()
            selector.spectrum()
            selector.annotated_frames()
            selector.empty_frames()
            selector.un_annotated_frames()
            selector.qa_change_requested_frames()
            selector.qa_approved_frames()
            selector.qa_pending_frames()
            selector.flagged_frames()
            selector.full_res_mp4_url()
            selector.full_res_mp4_status()
