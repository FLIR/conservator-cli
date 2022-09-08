import sgqlc.types
import FLIR.conservator.generated.date


schema = sgqlc.types.Schema()


########################################################################
# Scalars and Enumerations
########################################################################
class AclMeta(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("owner",)


class AllowedLabelCharacters(sgqlc.types.Scalar):
    __schema__ = schema


class AnnotationImportState(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("completed", "failed", "processing", "retrying", "uploading")


class AnnotationSourceType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("human", "machine", "unknown")


class ArrayUpdateMode(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("add", "remove", "replace")


class AttributePrototypeType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("checklist", "dropdown", "number", "radio", "text")


class AttributeSource(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("Conservator", "Labelbox", "Unknown")


Boolean = sgqlc.types.Boolean


class CollectionSQARunStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("complete", "failed", "pending", "processing", "queued")


class DatasheetJobState(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = (
        "completed",
        "created",
        "downloading",
        "failed",
        "nntc_dynamic",
        "nntc_static",
        "processing",
        "queued",
        "received",
        "uploading",
    )


Date = FLIR.conservator.generated.date.Date


class DuplicateAction(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("overwrite", "skip")


class FavoriteAssetType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("collection", "dataset", "datasetFrame", "frame", "image", "video")


Float = sgqlc.types.Float


class GraphqlID(sgqlc.types.Scalar):
    __schema__ = schema


class GroupType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("admin", "common", "everyone")


ID = sgqlc.types.ID

Int = sgqlc.types.Int


class Md5Exists(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("False", "Invalid", "True")


class Md5String(sgqlc.types.Scalar):
    __schema__ = schema


class Spectrum(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("Mixed", "Other", "RGB", "Thermal", "Unknown")


String = sgqlc.types.String


class StringLowerCase(sgqlc.types.Scalar):
    __schema__ = schema


class VideoState(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = (
        "adminFailed",
        "completed",
        "failed",
        "processing",
        "retrying",
        "uploading",
    )


class labelTools(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("bounding_box", "point", "polygon")


########################################################################
# Input Objects
########################################################################
class AcceptAnnotation(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "labels",
        "bounding_box",
        "bounding_polygon",
        "point",
        "source",
        "target_id",
        "attributes",
        "label_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    bounding_box = sgqlc.types.Field("BoundingBoxInput", graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("InputPoint")),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field("InputPoint", graphql_name="point")
    source = sgqlc.types.Field(
        sgqlc.types.non_null("InputSource"), graphql_name="source"
    )
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("AddAttributeInput")),
        graphql_name="attributes",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")


class AcceptDatasetAnnotationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "original_id",
        "dataset_frame_id",
        "labels",
        "label_id",
        "bounding_box",
        "bounding_polygon",
        "point",
        "target_id",
        "attributes",
    )
    original_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="originalId"
    )
    dataset_frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetFrameId"
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    bounding_box = sgqlc.types.Field("BoundingBoxInput", graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("InputPoint")),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field("InputPoint", graphql_name="point")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("AddAttributeInput")),
        graphql_name="attributes",
    )


class AclInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("object_id", "admin", "write", "read")
    object_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="objectId"
    )
    admin = sgqlc.types.Field("AclTypeInput", graphql_name="admin")
    write = sgqlc.types.Field("AclTypeInput", graphql_name="write")
    read = sgqlc.types.Field("AclTypeInput", graphql_name="read")


class AclTypeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("user_ids", "group_ids", "meta")
    user_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)), graphql_name="userIds"
    )
    group_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)), graphql_name="groupIds"
    )
    meta = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(AclMeta)), graphql_name="meta"
    )


class AddAssociatedFrameInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("frame_id", "dataset_frame_id", "spectrum")
    frame_id = sgqlc.types.Field(GraphqlID, graphql_name="frameId")
    dataset_frame_id = sgqlc.types.Field(GraphqlID, graphql_name="datasetFrameId")
    spectrum = sgqlc.types.Field(
        sgqlc.types.non_null(Spectrum), graphql_name="spectrum"
    )


class AddAttributeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "name",
        "value",
        "attribute_prototype_id",
        "type",
        "options",
        "source",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    attribute_prototype_id = sgqlc.types.Field(
        GraphqlID, graphql_name="attributePrototypeId"
    )
    type = sgqlc.types.Field(
        sgqlc.types.non_null(AttributePrototypeType), graphql_name="type"
    )
    options = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="options")
    source = sgqlc.types.Field(
        sgqlc.types.non_null(AttributeSource), graphql_name="source"
    )


class AddAttributePrototypeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "type", "is_required", "options")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    type = sgqlc.types.Field(
        sgqlc.types.non_null(AttributePrototypeType), graphql_name="type"
    )
    is_required = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isRequired"
    )
    options = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="options")


class AddFramesToDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_id", "frame_ids", "overwrite")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    frame_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="frameIds",
    )
    overwrite = sgqlc.types.Field(Boolean, graphql_name="overwrite")


class AddGroupMembersInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("group_id", "member_ids")
    group_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="groupId"
    )
    member_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="memberIds",
    )


class AddSegmentsToDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_id", "segment_ids", "frame_skip", "overwrite")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    segment_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="segmentIds",
    )
    frame_skip = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="frameSkip")
    overwrite = sgqlc.types.Field(Boolean, graphql_name="overwrite")


class AddVideosToDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_id", "video_ids", "frame_skip", "overwrite")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    video_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="videoIds",
    )
    frame_skip = sgqlc.types.Field(Int, graphql_name="frameSkip")
    overwrite = sgqlc.types.Field(Boolean, graphql_name="overwrite")


class AnnotationCreate(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "labels",
        "label_id",
        "point",
        "bounding_box",
        "bounding_polygon",
        "target_id",
        "custom",
        "source",
        "attributes",
        "qa_status",
        "qa_status_note",
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    point = sgqlc.types.Field("InputPoint", graphql_name="point")
    bounding_box = sgqlc.types.Field("BoundingBoxInput", graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("InputPoint")),
        graphql_name="boundingPolygon",
    )
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    custom = sgqlc.types.Field(String, graphql_name="custom")
    source = sgqlc.types.Field("AnnotationSourceInput", graphql_name="source")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(AddAttributeInput), graphql_name="attributes"
    )
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class AnnotationSourceInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("type", "meta")
    type = sgqlc.types.Field(
        sgqlc.types.non_null(AnnotationSourceType), graphql_name="type"
    )
    meta = sgqlc.types.Field("AnnotationSourceMetaInput", graphql_name="meta")


class AnnotationSourceMetaInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("tool", "classifier_id", "original_id", "comment", "user")
    tool = sgqlc.types.Field(String, graphql_name="tool")
    classifier_id = sgqlc.types.Field(String, graphql_name="classifierId")
    original_id = sgqlc.types.Field(GraphqlID, graphql_name="originalId")
    comment = sgqlc.types.Field(String, graphql_name="comment")
    user = sgqlc.types.Field(GraphqlID, graphql_name="user")


class AnnotationUpdate(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "labels",
        "label_id",
        "bounding_box",
        "bounding_polygon",
        "point",
        "target_id",
        "qa_status",
        "qa_status_note",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    labels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters)),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    bounding_box = sgqlc.types.Field("BoundingBoxInput", graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("InputPoint")),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field("InputPoint", graphql_name="point")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class ArchiveDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")


class BoundingBoxInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("x", "y", "w", "h")
    x = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="x")
    y = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="y")
    w = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="w")
    h = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="h")


class CloneGroupOptions(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("should_clone_permissions", "should_clone_members")
    should_clone_permissions = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="shouldClonePermissions"
    )
    should_clone_members = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="shouldCloneMembers"
    )


class CreateCollectionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "parent_id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    parent_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="parentId"
    )


class CreateDatasetAnnotationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "dataset_frame_id",
        "labels",
        "label_id",
        "bounding_box",
        "bounding_polygon",
        "point",
        "target_id",
        "source",
        "attributes",
        "custom",
        "qa_status",
        "qa_status_note",
    )
    dataset_frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetFrameId"
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    bounding_box = sgqlc.types.Field(BoundingBoxInput, graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("InputPoint")),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field("InputPoint", graphql_name="point")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    source = sgqlc.types.Field(AnnotationSourceInput, graphql_name="source")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(AddAttributeInput), graphql_name="attributes"
    )
    custom = sgqlc.types.Field(String, graphql_name="custom")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class CreateDatasetFrameInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "frame_id",
        "video_id",
        "frame_index",
        "preview_width",
        "preview_height",
        "width",
        "height",
        "is_empty",
        "is_flagged",
        "description",
        "location",
        "tags",
        "spectrum",
        "md5",
        "file_size",
        "analytics_md5",
        "analytics_file_size",
        "preview_md5",
        "preview_file_size",
        "custom_metadata",
        "labelbox_metadata",
        "labelbox_data_row_id",
        "qa_status",
        "qa_status_note",
        "associated_frames",
    )
    id = sgqlc.types.Field(GraphqlID, graphql_name="id")
    frame_id = sgqlc.types.Field(GraphqlID, graphql_name="frameId")
    video_id = sgqlc.types.Field(GraphqlID, graphql_name="videoId")
    frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameIndex"
    )
    preview_width = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewWidth"
    )
    preview_height = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewHeight"
    )
    width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="width")
    height = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="height")
    is_empty = sgqlc.types.Field(Boolean, graphql_name="isEmpty")
    is_flagged = sgqlc.types.Field(Boolean, graphql_name="isFlagged")
    description = sgqlc.types.Field(String, graphql_name="description")
    location = sgqlc.types.Field(String, graphql_name="location")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    spectrum = sgqlc.types.Field(Spectrum, graphql_name="spectrum")
    md5 = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="md5")
    file_size = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="fileSize")
    analytics_md5 = sgqlc.types.Field(String, graphql_name="analyticsMd5")
    analytics_file_size = sgqlc.types.Field(Float, graphql_name="analyticsFileSize")
    preview_md5 = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="previewMd5"
    )
    preview_file_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="previewFileSize"
    )
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    labelbox_metadata = sgqlc.types.Field(String, graphql_name="labelboxMetadata")
    labelbox_data_row_id = sgqlc.types.Field(String, graphql_name="labelboxDataRowId")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    associated_frames = sgqlc.types.Field(
        sgqlc.types.list_of(AddAssociatedFrameInput), graphql_name="associatedFrames"
    )


class CreateDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "name", "collection_ids")
    id = sgqlc.types.Field(GraphqlID, graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    collection_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="collectionIds"
    )


class CreateGroupInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "name",
        "member_ids",
        "notes",
        "conservator_insights_license_key",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    member_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="memberIds"
    )
    notes = sgqlc.types.Field(String, graphql_name="notes")
    conservator_insights_license_key = sgqlc.types.Field(
        String, graphql_name="conservatorInsightsLicenseKey"
    )


class CreateSegmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("video_id", "start_frame_index", "end_frame_index")
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    start_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="startFrameIndex"
    )
    end_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="endFrameIndex"
    )


class DatasetFrameMetadataInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "mode",
        "description",
        "custom_metadata",
        "location",
        "tags",
        "spectrum",
    )
    mode = sgqlc.types.Field(ArrayUpdateMode, graphql_name="mode")
    description = sgqlc.types.Field(String, graphql_name="description")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    location = sgqlc.types.Field(String, graphql_name="location")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    spectrum = sgqlc.types.Field(Spectrum, graphql_name="spectrum")


class DeleteCollectionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")


class DeleteDatasetAnnotationsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_frame_id", "dataset_annotation_ids")
    dataset_frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetFrameId"
    )
    dataset_annotation_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="datasetAnnotationIds",
    )


class DeleteDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")


class DeleteGroupInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("group_id",)
    group_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="groupId"
    )


class DeleteSegmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")


class FileLockerFileInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("url", "name", "is_removed")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")


class FilterItemInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "value")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class FlagDatasetFrameInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_frame_id",)
    dataset_frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetFrameId"
    )


class FrameFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "has",
        "datasets",
        "tags",
        "uploaded_after",
        "uploaded_before",
        "frame_step",
        "video_id",
        "frame_index",
        "is_key_frame",
    )
    has = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="has"
    )
    datasets = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)),
        graphql_name="datasets",
    )
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    uploaded_after = sgqlc.types.Field(Date, graphql_name="uploadedAfter")
    uploaded_before = sgqlc.types.Field(Date, graphql_name="uploadedBefore")
    frame_step = sgqlc.types.Field(Int, graphql_name="frameStep")
    video_id = sgqlc.types.Field(GraphqlID, graphql_name="videoId")
    frame_index = sgqlc.types.Field(Int, graphql_name="frameIndex")
    is_key_frame = sgqlc.types.Field(Boolean, graphql_name="isKeyFrame")


class FrameIdByOffsetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("video_id", "current_index", "offset", "search_text")
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    current_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="currentIndex"
    )
    offset = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="offset")
    search_text = sgqlc.types.Field(String, graphql_name="searchText")


class FrameMetadataInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "mode",
        "description",
        "custom_metadata",
        "location",
        "tags",
        "spectrum",
    )
    mode = sgqlc.types.Field(ArrayUpdateMode, graphql_name="mode")
    description = sgqlc.types.Field(String, graphql_name="description")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    location = sgqlc.types.Field(String, graphql_name="location")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    spectrum = sgqlc.types.Field(Spectrum, graphql_name="spectrum")


class FullVideoInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "created_at",
        "modified_at",
        "annotation_import_state_modified_at",
        "filename",
        "collections",
        "state",
        "spectrum",
        "user_id",
        "uploaded_by",
        "file_locker_files",
        "full_res_mp4_status",
        "preview_generation_status",
        "url",
        "annotation_count",
        "prediction_count",
        "process_video_error_message",
        "annotation_import_state",
        "annotation_import_error_message",
        "md5",
        "file_size",
        "preview_md5",
        "preview_file_size",
        "preview_video_url",
        "name",
        "description",
        "location",
        "width",
        "height",
        "tags",
        "filmed_at",
        "duration",
        "frame_rate",
        "bit_depth",
        "raw_exif",
        "custom_metadata",
        "segments",
        "analytics_state",
        "cover_image_frame_id",
        "object_detect_error",
        "process_state",
        "full_res_mp4_url",
    )
    id = sgqlc.types.Field(GraphqlID, graphql_name="id")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Float, graphql_name="modifiedAt")
    annotation_import_state_modified_at = sgqlc.types.Field(
        Date, graphql_name="annotationImportStateModifiedAt"
    )
    filename = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="filename")
    collections = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="collections"
    )
    state = sgqlc.types.Field(sgqlc.types.non_null(VideoState), graphql_name="state")
    spectrum = sgqlc.types.Field(
        sgqlc.types.non_null(Spectrum), graphql_name="spectrum"
    )
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    uploaded_by = sgqlc.types.Field(GraphqlID, graphql_name="uploadedBy")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of(FileLockerFileInput), graphql_name="fileLockerFiles"
    )
    full_res_mp4_status = sgqlc.types.Field(String, graphql_name="fullResMp4Status")
    preview_generation_status = sgqlc.types.Field(
        String, graphql_name="previewGenerationStatus"
    )
    url = sgqlc.types.Field(String, graphql_name="url")
    annotation_count = sgqlc.types.Field(Int, graphql_name="annotationCount")
    prediction_count = sgqlc.types.Field(Int, graphql_name="predictionCount")
    process_video_error_message = sgqlc.types.Field(
        String, graphql_name="processVideoErrorMessage"
    )
    annotation_import_state = sgqlc.types.Field(
        String, graphql_name="annotationImportState"
    )
    annotation_import_error_message = sgqlc.types.Field(
        String, graphql_name="annotationImportErrorMessage"
    )
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    file_size = sgqlc.types.Field(Float, graphql_name="fileSize")
    preview_md5 = sgqlc.types.Field(String, graphql_name="previewMd5")
    preview_file_size = sgqlc.types.Field(Float, graphql_name="previewFileSize")
    preview_video_url = sgqlc.types.Field(String, graphql_name="previewVideoUrl")
    name = sgqlc.types.Field(String, graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    location = sgqlc.types.Field(String, graphql_name="location")
    width = sgqlc.types.Field(Int, graphql_name="width")
    height = sgqlc.types.Field(Int, graphql_name="height")
    tags = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="tags")
    filmed_at = sgqlc.types.Field(Date, graphql_name="filmedAt")
    duration = sgqlc.types.Field(String, graphql_name="duration")
    frame_rate = sgqlc.types.Field(Float, graphql_name="frameRate")
    bit_depth = sgqlc.types.Field(Int, graphql_name="bitDepth")
    raw_exif = sgqlc.types.Field(String, graphql_name="rawExif")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    segments = sgqlc.types.Field(
        sgqlc.types.list_of("SegmentInput"), graphql_name="segments"
    )
    analytics_state = sgqlc.types.Field(String, graphql_name="analyticsState")
    cover_image_frame_id = sgqlc.types.Field(
        GraphqlID, graphql_name="coverImageFrameId"
    )
    object_detect_error = sgqlc.types.Field(String, graphql_name="objectDetectError")
    process_state = sgqlc.types.Field("ProcessStateInput", graphql_name="processState")
    full_res_mp4_url = sgqlc.types.Field(String, graphql_name="fullResMp4Url")


class InputPoint(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("x", "y")
    x = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="x")
    y = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="y")


class InputSource(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("type",)
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="type")


class InterpolationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("video_id", "start_index", "end_index")
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    start_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="startIndex"
    )
    end_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="endIndex")


class LabelInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "label_set_id", "color", "tool")
    name = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedLabelCharacters), graphql_name="name"
    )
    label_set_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="labelSetId"
    )
    color = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="color")
    tool = sgqlc.types.Field(sgqlc.types.non_null(labelTools), graphql_name="tool")


class LabelUpdate(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "name", "color", "label_set_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(AllowedLabelCharacters, graphql_name="name")
    color = sgqlc.types.Field(String, graphql_name="color")
    label_set_id = sgqlc.types.Field(GraphqlID, graphql_name="labelSetId")


class MergeDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_ids", "merged_dataset_name")
    dataset_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="datasetIds",
    )
    merged_dataset_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="mergedDatasetName"
    )


class MetadataInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "owner",
        "name",
        "description",
        "location",
        "tags",
        "spectrum",
        "asset_type",
        "attached_label_set_ids",
        "allow_annotations_outside_frame",
        "allow_duplicate_target_id",
    )
    owner = sgqlc.types.Field(GraphqlID, graphql_name="owner")
    name = sgqlc.types.Field(String, graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    location = sgqlc.types.Field(String, graphql_name="location")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    spectrum = sgqlc.types.Field(Spectrum, graphql_name="spectrum")
    asset_type = sgqlc.types.Field(Spectrum, graphql_name="assetType")
    attached_label_set_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="attachedLabelSetIds"
    )
    allow_annotations_outside_frame = sgqlc.types.Field(
        Boolean, graphql_name="allowAnnotationsOutsideFrame"
    )
    allow_duplicate_target_id = sgqlc.types.Field(
        Boolean, graphql_name="allowDuplicateTargetId"
    )


class ModifyAttributeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "value")
    name = sgqlc.types.Field(String, graphql_name="name")
    value = sgqlc.types.Field(String, graphql_name="value")


class ModifyAttributePrototypeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("name", "type", "is_required", "options")
    name = sgqlc.types.Field(String, graphql_name="name")
    type = sgqlc.types.Field(AttributePrototypeType, graphql_name="type")
    is_required = sgqlc.types.Field(Boolean, graphql_name="isRequired")
    options = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="options")


class MoveAnnotationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "bounding_box", "bounding_polygon", "point")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    bounding_box = sgqlc.types.Field(BoundingBoxInput, graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(InputPoint)),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field(InputPoint, graphql_name="point")


class MoveAnnotationsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("frame_id", "annotations")
    frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="frameId"
    )
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(MoveAnnotationInput))
        ),
        graphql_name="annotations",
    )


class MoveAssetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("asset_id", "from_collection", "to_collection")
    asset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="assetId"
    )
    from_collection = sgqlc.types.Field(GraphqlID, graphql_name="fromCollection")
    to_collection = sgqlc.types.Field(GraphqlID, graphql_name="toCollection")


class PredictionCreate(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("labels", "bounding_box", "classifier_id", "target_id", "custom")
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    bounding_box = sgqlc.types.Field(
        sgqlc.types.non_null(BoundingBoxInput), graphql_name="boundingBox"
    )
    classifier_id = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="classifierId"
    )
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    custom = sgqlc.types.Field(String, graphql_name="custom")


class ProcessStateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("retry_count", "correlation_id", "container_name", "message")
    retry_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="retryCount"
    )
    correlation_id = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="correlationId"
    )
    container_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="containerName"
    )
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="message")


class RemoveAnnotationsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("frame_id", "annotation_ids")
    frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="frameId"
    )
    annotation_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="annotationIds",
    )


class RemoveAssociatedFrameInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("frame_id", "dataset_frame_id")
    frame_id = sgqlc.types.Field(GraphqlID, graphql_name="frameId")
    dataset_frame_id = sgqlc.types.Field(GraphqlID, graphql_name="datasetFrameId")


class RemoveFramesFromDatasetByIdsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_id", "ids")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="ids",
    )


class RemoveFramesFromDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_id", "frame_ids")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    frame_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="frameIds",
    )


class RemoveGroupMembersInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("group_id", "member_ids")
    group_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="groupId"
    )
    member_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="memberIds",
    )


class SegmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "start_frame_index",
        "end_frame_index",
        "created_at",
        "modified_at",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    start_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="startFrameIndex"
    )
    end_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="endFrameIndex"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )


class UnflagDatasetFrameInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("dataset_frame_id",)
    dataset_frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetFrameId"
    )


class UpdateCollectionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "name", "default_classifier", "description")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(String, graphql_name="name")
    default_classifier = sgqlc.types.Field(String, graphql_name="defaultClassifier")
    description = sgqlc.types.Field(String, graphql_name="description")


class UpdateDatasetAnnotationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "dataset_annotation_id",
        "labels",
        "label_id",
        "bounding_box",
        "bounding_polygon",
        "point",
        "target_id",
        "qa_status",
        "qa_status_note",
    )
    dataset_annotation_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetAnnotationId"
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    bounding_box = sgqlc.types.Field(BoundingBoxInput, graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(InputPoint)),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field(InputPoint, graphql_name="point")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class UpdateDatasetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "owner",
        "name",
        "is_locked",
        "notes",
        "tags",
        "attached_label_set_ids",
        "description",
        "allow_annotations_outside_frame",
        "allow_duplicate_target_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    owner = sgqlc.types.Field(GraphqlID, graphql_name="owner")
    name = sgqlc.types.Field(String, graphql_name="name")
    is_locked = sgqlc.types.Field(Boolean, graphql_name="isLocked")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="tags"
    )
    attached_label_set_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="attachedLabelSetIds"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    allow_annotations_outside_frame = sgqlc.types.Field(
        Boolean, graphql_name="allowAnnotationsOutsideFrame"
    )
    allow_duplicate_target_id = sgqlc.types.Field(
        Boolean, graphql_name="allowDuplicateTargetId"
    )


class UpdateDatasetQaStatusNoteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "qa_status_note")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class UpdateGroupInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "group_id",
        "name",
        "member_ids",
        "notes",
        "conservator_insights_license_key",
    )
    group_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="groupId"
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    member_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)), graphql_name="memberIds"
    )
    notes = sgqlc.types.Field(String, graphql_name="notes")
    conservator_insights_license_key = sgqlc.types.Field(
        String, graphql_name="conservatorInsightsLicenseKey"
    )


class UpdateGroupNoteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "notes")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    notes = sgqlc.types.Field(String, graphql_name="notes")


class UpdateLabelsetNoteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "notes")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    notes = sgqlc.types.Field(String, graphql_name="notes")


class UpdateQaStatusNoteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "qa_status_note")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")


class UpdateSegmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "start_frame_index", "end_frame_index")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    start_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="startFrameIndex"
    )
    end_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="endFrameIndex"
    )


class UpdateUserNoteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "notes")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    notes = sgqlc.types.Field(String, graphql_name="notes")


########################################################################
# Output Objects and Interfaces
########################################################################
class Acl(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("admin", "write", "read")
    admin = sgqlc.types.Field("AclType", graphql_name="admin")
    write = sgqlc.types.Field("AclType", graphql_name="write")
    read = sgqlc.types.Field("AclType", graphql_name="read")


class AclGroups(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("users", "groups")
    users = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("User")), graphql_name="users"
    )
    groups = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("Group")), graphql_name="groups"
    )


class AclPermissionLevels(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("read", "write", "admin")
    read = sgqlc.types.Field(AclGroups, graphql_name="read")
    write = sgqlc.types.Field(AclGroups, graphql_name="write")
    admin = sgqlc.types.Field(AclGroups, graphql_name="admin")


class AclType(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("user_ids", "group_ids", "meta")
    user_ids = sgqlc.types.Field(sgqlc.types.list_of("User"), graphql_name="userIds")
    group_ids = sgqlc.types.Field(sgqlc.types.list_of("Group"), graphql_name="groupIds")
    meta = sgqlc.types.Field(sgqlc.types.list_of(AclMeta), graphql_name="meta")


class AllowedDomain(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "domain",
        "default_group",
        "created_at",
        "modified_at",
        "is_removed",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    domain = sgqlc.types.Field(String, graphql_name="domain")
    default_group = sgqlc.types.Field(String, graphql_name="defaultGroup")
    created_at = sgqlc.types.Field(Date, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Date, graphql_name="modifiedAt")
    is_removed = sgqlc.types.Field(String, graphql_name="isRemoved")


class Annotation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "target_id",
        "label",
        "labels",
        "label_id",
        "color",
        "bounding_box",
        "bounding_polygon",
        "source",
        "point",
        "custom_metadata",
        "attributes",
        "qa_status",
        "qa_status_note",
        "labelbox_metadata",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    label = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedLabelCharacters), graphql_name="label"
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    color = sgqlc.types.Field(String, graphql_name="color")
    bounding_box = sgqlc.types.Field("BoundingBox", graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("Point")),
        graphql_name="boundingPolygon",
    )
    source = sgqlc.types.Field(sgqlc.types.non_null("Source"), graphql_name="source")
    point = sgqlc.types.Field("Point", graphql_name="point")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of("Attribute"), graphql_name="attributes"
    )
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    labelbox_metadata = sgqlc.types.Field(String, graphql_name="labelboxMetadata")


class AnnotationMeta(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "tool",
        "classifier_id",
        "original_id",
        "comment",
        "user",
        "interpolated",
    )
    tool = sgqlc.types.Field(String, graphql_name="tool")
    classifier_id = sgqlc.types.Field(String, graphql_name="classifierId")
    original_id = sgqlc.types.Field(GraphqlID, graphql_name="originalId")
    comment = sgqlc.types.Field(String, graphql_name="comment")
    user = sgqlc.types.Field(GraphqlID, graphql_name="user")
    interpolated = sgqlc.types.Field(Boolean, graphql_name="interpolated")


class AnnotationStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("total", "machine_annotations", "human_annotations")
    total = sgqlc.types.Field(Int, graphql_name="total")
    machine_annotations = sgqlc.types.Field(
        "MachineAnnotationStats", graphql_name="machineAnnotations"
    )
    human_annotations = sgqlc.types.Field(
        "HumanAnnotationStats", graphql_name="humanAnnotations"
    )


class AssociatedFrame(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("url", "spectrum", "description")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    spectrum = sgqlc.types.Field(
        sgqlc.types.non_null(Spectrum), graphql_name="spectrum"
    )
    description = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="description"
    )


class Attribute(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "name",
        "value",
        "attribute_prototype_id",
        "type",
        "options",
        "source",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    attribute_prototype_id = sgqlc.types.Field(
        GraphqlID, graphql_name="attributePrototypeId"
    )
    type = sgqlc.types.Field(AttributePrototypeType, graphql_name="type")
    options = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="options")
    source = sgqlc.types.Field(
        sgqlc.types.non_null(AttributeSource), graphql_name="source"
    )


class AttributePrototype(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "name", "type", "is_required", "options")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    type = sgqlc.types.Field(
        sgqlc.types.non_null(AttributePrototypeType), graphql_name="type"
    )
    is_required = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isRequired"
    )
    options = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="options")


class AuthPayload(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("session_id", "user", "error", "error_args")
    session_id = sgqlc.types.Field(String, graphql_name="sessionId")
    user = sgqlc.types.Field("User", graphql_name="user")
    error = sgqlc.types.Field(String, graphql_name="error")
    error_args = sgqlc.types.Field(
        sgqlc.types.list_of("ErrorArg"), graphql_name="errorArgs"
    )


class BoundingBox(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("x", "y", "w", "h")
    x = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="x")
    y = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="y")
    w = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="w")
    h = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="h")


class Classifier(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "name", "use_for_object_detect")
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    use_for_object_detect = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="useForObjectDetect"
    )


class Collection(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "parent_id",
        "project_id",
        "name",
        "is_parent",
        "children",
        "acl",
        "user_id",
        "user_id_name",
        "created_by",
        "created_by_name",
        "created_byemail",
        "created_at",
        "modified_at",
        "video_count",
        "recursive_video_count",
        "dataset_count",
        "recursive_dataset_count",
        "image_count",
        "recursive_image_count",
        "child_count",
        "recursive_child_count",
        "default_classifier",
        "path",
        "file_locker_files",
        "cover_image_url",
        "description",
        "word_cloud_url",
        "parents",
        "child_ids",
        "readme",
        "is_favorite",
        "favorite_count",
        "owner",
        "owner_email",
        "has_write_access",
        "has_admin_access",
        "video_ids",
        "image_ids",
        "dataset_ids",
        "sqa_run_status",
        "sqa_run_status_message",
        "sqa_run_error_message",
        "recalculate_stats_state",
        "recalculate_stats_error",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    parent_id = sgqlc.types.Field(GraphqlID, graphql_name="parentId")
    project_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="projectId"
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_parent = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isParent"
    )
    children = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Collection")), graphql_name="children"
    )
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    user_id_name = sgqlc.types.Field(String, graphql_name="userIdName")
    created_by = sgqlc.types.Field(String, graphql_name="createdBy")
    created_by_name = sgqlc.types.Field(String, graphql_name="createdByName")
    created_byemail = sgqlc.types.Field(String, graphql_name="createdByemail")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Float, graphql_name="modifiedAt")
    video_count = sgqlc.types.Field(Int, graphql_name="videoCount")
    recursive_video_count = sgqlc.types.Field(Int, graphql_name="recursiveVideoCount")
    dataset_count = sgqlc.types.Field(Int, graphql_name="datasetCount")
    recursive_dataset_count = sgqlc.types.Field(
        Int, graphql_name="recursiveDatasetCount"
    )
    image_count = sgqlc.types.Field(Int, graphql_name="imageCount")
    recursive_image_count = sgqlc.types.Field(Int, graphql_name="recursiveImageCount")
    child_count = sgqlc.types.Field(Int, graphql_name="childCount")
    recursive_child_count = sgqlc.types.Field(Int, graphql_name="recursiveChildCount")
    default_classifier = sgqlc.types.Field(Classifier, graphql_name="defaultClassifier")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of("file"), graphql_name="fileLockerFiles"
    )
    cover_image_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="coverImageUrl"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    word_cloud_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="wordCloudUrl"
    )
    parents = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Parent")), graphql_name="parents"
    )
    child_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="childIds"
    )
    readme = sgqlc.types.Field(String, graphql_name="readme")
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    owner_email = sgqlc.types.Field(String, graphql_name="ownerEmail")
    has_write_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasWriteAccess"
    )
    has_admin_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasAdminAccess"
    )
    video_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="videoIds"
    )
    image_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="imageIds"
    )
    dataset_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="datasetIds"
    )
    sqa_run_status = sgqlc.types.Field(String, graphql_name="sqaRunStatus")
    sqa_run_status_message = sgqlc.types.Field(
        String, graphql_name="sqaRunStatusMessage"
    )
    sqa_run_error_message = sgqlc.types.Field(String, graphql_name="sqaRunErrorMessage")
    recalculate_stats_state = sgqlc.types.Field(
        String, graphql_name="recalculateStatsState"
    )
    recalculate_stats_error = sgqlc.types.Field(
        String, graphql_name="recalculateStatsError"
    )


class CollectionSQARun(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "collection_id",
        "created_at",
        "modified_at",
        "created_by",
        "status",
        "status_message",
        "error_message",
        "completed_at",
        "email_notification",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    collection_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="collectionId"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )
    created_by = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="createdBy"
    )
    status = sgqlc.types.Field(
        sgqlc.types.non_null(CollectionSQARunStatus), graphql_name="status"
    )
    status_message = sgqlc.types.Field(String, graphql_name="statusMessage")
    error_message = sgqlc.types.Field(String, graphql_name="errorMessage")
    completed_at = sgqlc.types.Field(Float, graphql_name="completedAt")
    email_notification = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="emailNotification"
    )


class Commit(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "_id",
        "author_name",
        "author_email",
        "size",
        "raw_message",
        "short_message",
        "commit_date",
        "tree",
        "parents",
        "version_note",
        "has_datasheets",
        "is_datasheet_job_running",
    )
    _id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="_id")
    author_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="authorName"
    )
    author_email = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="authorEmail"
    )
    size = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="size")
    raw_message = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="rawMessage"
    )
    short_message = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="shortMessage"
    )
    commit_date = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="commitDate"
    )
    tree = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="tree")
    parents = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="parents")
    version_note = sgqlc.types.Field(String, graphql_name="versionNote")
    has_datasheets = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasDatasheets"
    )
    is_datasheet_job_running = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isDatasheetJobRunning"
    )


class ConservatorStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "total_video_count",
        "total_image_count",
        "total_dataset_count",
        "total_video_frame_count",
        "total_dataset_frame_count",
        "total_user_count",
        "total_group_count",
        "total_file_size",
        "from_",
        "to",
        "created_at",
        "total_video_annotations",
        "total_dataset_annotations",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    total_video_count = sgqlc.types.Field(Int, graphql_name="totalVideoCount")
    total_image_count = sgqlc.types.Field(Int, graphql_name="totalImageCount")
    total_dataset_count = sgqlc.types.Field(Int, graphql_name="totalDatasetCount")
    total_video_frame_count = sgqlc.types.Field(
        Int, graphql_name="totalVideoFrameCount"
    )
    total_dataset_frame_count = sgqlc.types.Field(
        Int, graphql_name="totalDatasetFrameCount"
    )
    total_user_count = sgqlc.types.Field(Int, graphql_name="totalUserCount")
    total_group_count = sgqlc.types.Field(Int, graphql_name="totalGroupCount")
    total_file_size = sgqlc.types.Field(Float, graphql_name="totalFileSize")
    from_ = sgqlc.types.Field(Float, graphql_name="from")
    to = sgqlc.types.Field(Float, graphql_name="to")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    total_video_annotations = sgqlc.types.Field(
        AnnotationStats, graphql_name="totalVideoAnnotations"
    )
    total_dataset_annotations = sgqlc.types.Field(
        AnnotationStats, graphql_name="totalDatasetAnnotations"
    )


class CopyDatasetAnnotationsResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("created", "skipped", "dataset_frame")
    created = sgqlc.types.Field(Int, graphql_name="created")
    skipped = sgqlc.types.Field(Int, graphql_name="skipped")
    dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null("DatasetFrame"), graphql_name="datasetFrame"
    )


class CopyVideoAnnotationsResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("skipped", "created", "frame")
    skipped = sgqlc.types.Field(Int, graphql_name="skipped")
    created = sgqlc.types.Field(Int, graphql_name="created")
    frame = sgqlc.types.Field(sgqlc.types.non_null("Frame"), graphql_name="frame")


class Dataset(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "user_id",
        "thumbnail_url",
        "cover_image_url",
        "cover_image_frame_id",
        "name",
        "is_locked",
        "frames",
        "frame_count",
        "video_count",
        "highest_target_id",
        "notes",
        "archive_url",
        "archived_at",
        "archive_state",
        "archive_progress",
        "created_at",
        "modified_at",
        "tags",
        "acl",
        "shared_with",
        "creation_status",
        "metadata_processing_state",
        "metadata_processing_error",
        "object_detect_state",
        "object_detect_batches_total",
        "object_detect_batches_done",
        "object_detect_error",
        "repository",
        "custom_metadata",
        "collections",
        "is_favorite",
        "favorite_count",
        "attached_label_set_ids",
        "attached_label_sets",
        "labelbox_project_id",
        "labelbox_import_state",
        "labelbox_export_state",
        "labelbox_sync_state",
        "labelbox_remove_state",
        "git_commit_state",
        "file_locker_files",
        "annotations_human_count",
        "annotations_machine_count",
        "readme",
        "labelbox_export_frames_processed",
        "labelbox_export_total_frames",
        "labelbox_import_frames_processed",
        "labelbox_import_total_frames",
        "labelbox_sync_frames_processed",
        "labelbox_sync_total_frames",
        "annotated_frames",
        "empty_frames",
        "un_annotated_frames",
        "owner",
        "owner_email",
        "qa_change_requested_frames",
        "qa_approved_frames",
        "qa_pending_frames",
        "flagged_frames",
        "prediction_label_data",
        "annotation_label_data",
        "inherited_acl",
        "has_write_access",
        "has_admin_access",
        "description",
        "video_ids",
        "preview_video_url",
        "preview_video_status",
        "recalculate_stats_state",
        "allow_annotations_outside_frame",
        "allow_duplicate_target_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    thumbnail_url = sgqlc.types.Field(String, graphql_name="thumbnailUrl")
    cover_image_url = sgqlc.types.Field(String, graphql_name="coverImageUrl")
    cover_image_frame_id = sgqlc.types.Field(
        GraphqlID, graphql_name="coverImageFrameId"
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_locked = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isLocked"
    )
    frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("DatasetFrame"))),
        graphql_name="frames",
        args=sgqlc.types.ArgDict(
            (
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameCount"
    )
    video_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="videoCount"
    )
    highest_target_id = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="highestTargetId"
    )
    notes = sgqlc.types.Field(String, graphql_name="notes")
    archive_url = sgqlc.types.Field(String, graphql_name="archiveUrl")
    archived_at = sgqlc.types.Field(Date, graphql_name="archivedAt")
    archive_state = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="archiveState"
    )
    archive_progress = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="archiveProgress"
    )
    created_at = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Date, graphql_name="modifiedAt")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="tags"
    )
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    shared_with = sgqlc.types.Field(AclPermissionLevels, graphql_name="sharedWith")
    creation_status = sgqlc.types.Field(
        "DatasetCreationStatus", graphql_name="creationStatus"
    )
    metadata_processing_state = sgqlc.types.Field(
        String, graphql_name="metadataProcessingState"
    )
    metadata_processing_error = sgqlc.types.Field(
        String, graphql_name="metadataProcessingError"
    )
    object_detect_state = sgqlc.types.Field(String, graphql_name="objectDetectState")
    object_detect_batches_total = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesTotal"
    )
    object_detect_batches_done = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesDone"
    )
    object_detect_error = sgqlc.types.Field(String, graphql_name="objectDetectError")
    repository = sgqlc.types.Field("Repository", graphql_name="repository")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    collections = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)), graphql_name="collections"
    )
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    attached_label_set_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="attachedLabelSetIds"
    )
    attached_label_sets = sgqlc.types.Field(
        sgqlc.types.list_of("LabelSet"), graphql_name="attachedLabelSets"
    )
    labelbox_project_id = sgqlc.types.Field(String, graphql_name="labelboxProjectId")
    labelbox_import_state = sgqlc.types.Field(
        String, graphql_name="labelboxImportState"
    )
    labelbox_export_state = sgqlc.types.Field(
        String, graphql_name="labelboxExportState"
    )
    labelbox_sync_state = sgqlc.types.Field(String, graphql_name="labelboxSyncState")
    labelbox_remove_state = sgqlc.types.Field(
        String, graphql_name="labelboxRemoveState"
    )
    git_commit_state = sgqlc.types.Field(String, graphql_name="gitCommitState")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of("file"), graphql_name="fileLockerFiles"
    )
    annotations_human_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotationsHumanCount"
    )
    annotations_machine_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotationsMachineCount"
    )
    readme = sgqlc.types.Field(String, graphql_name="readme")
    labelbox_export_frames_processed = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxExportFramesProcessed"
    )
    labelbox_export_total_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxExportTotalFrames"
    )
    labelbox_import_frames_processed = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxImportFramesProcessed"
    )
    labelbox_import_total_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxImportTotalFrames"
    )
    labelbox_sync_frames_processed = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxSyncFramesProcessed"
    )
    labelbox_sync_total_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="labelboxSyncTotalFrames"
    )
    annotated_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotatedFrames"
    )
    empty_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="emptyFrames"
    )
    un_annotated_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="unAnnotatedFrames"
    )
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    owner_email = sgqlc.types.Field(String, graphql_name="ownerEmail")
    qa_change_requested_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="qaChangeRequestedFrames"
    )
    qa_approved_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="qaApprovedFrames"
    )
    qa_pending_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="qaPendingFrames"
    )
    flagged_frames = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="flaggedFrames"
    )
    prediction_label_data = sgqlc.types.Field(
        sgqlc.types.list_of("labelCount"), graphql_name="predictionLabelData"
    )
    annotation_label_data = sgqlc.types.Field(
        sgqlc.types.list_of("labelCount"), graphql_name="annotationLabelData"
    )
    inherited_acl = sgqlc.types.Field(Acl, graphql_name="inheritedAcl")
    has_write_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasWriteAccess"
    )
    has_admin_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasAdminAccess"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    video_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="videoIds"
    )
    preview_video_url = sgqlc.types.Field(String, graphql_name="previewVideoUrl")
    preview_video_status = sgqlc.types.Field(String, graphql_name="previewVideoStatus")
    recalculate_stats_state = sgqlc.types.Field(
        String, graphql_name="recalculateStatsState"
    )
    allow_annotations_outside_frame = sgqlc.types.Field(
        Boolean, graphql_name="allowAnnotationsOutsideFrame"
    )
    allow_duplicate_target_id = sgqlc.types.Field(
        Boolean, graphql_name="allowDuplicateTargetId"
    )


class DatasetAnnotation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "target_id",
        "label",
        "labels",
        "label_id",
        "color",
        "bounding_box",
        "bounding_polygon",
        "point",
        "source",
        "custom_metadata",
        "attributes",
        "qa_status",
        "qa_status_note",
        "labelbox_metadata",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    target_id = sgqlc.types.Field(Int, graphql_name="targetId")
    label = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedLabelCharacters), graphql_name="label"
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(AllowedLabelCharacters))
        ),
        graphql_name="labels",
    )
    label_id = sgqlc.types.Field(GraphqlID, graphql_name="labelId")
    color = sgqlc.types.Field(String, graphql_name="color")
    bounding_box = sgqlc.types.Field(BoundingBox, graphql_name="boundingBox")
    bounding_polygon = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("Point")),
        graphql_name="boundingPolygon",
    )
    point = sgqlc.types.Field("Point", graphql_name="point")
    source = sgqlc.types.Field(sgqlc.types.non_null("Source"), graphql_name="source")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(Attribute), graphql_name="attributes"
    )
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    labelbox_metadata = sgqlc.types.Field(String, graphql_name="labelboxMetadata")


class DatasetCreationStatus(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("status", "progress", "error")
    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="status")
    progress = sgqlc.types.Field(String, graphql_name="progress")
    error = sgqlc.types.Field(String, graphql_name="error")


class DatasetFrame(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "owner",
        "dataset_id",
        "index",
        "frame_id",
        "video_id",
        "labelbox_data_row_id",
        "file_size",
        "frame_index",
        "url",
        "height",
        "width",
        "preview_url",
        "preview_height",
        "preview_width",
        "preview_file_size",
        "created_at",
        "modified_at",
        "next",
        "next5",
        "next100",
        "next_flag",
        "previous",
        "previous5",
        "previous100",
        "prev_flag",
        "video",
        "annotations",
        "is_flagged",
        "is_empty",
        "is_cover_image",
        "annotation_count",
        "is_favorite",
        "favorite_count",
        "prediction_label_data",
        "annotation_label_data",
        "human_annotation_count",
        "machine_annotation_count",
        "custom_metadata",
        "qa_status",
        "qa_status_note",
        "md5",
        "preview_md5",
        "analytics_md5",
        "analytics_file_size",
        "location",
        "description",
        "spectrum",
        "tags",
        "dataset_frame_name",
        "attributes",
        "dataset_name",
        "associated_frames",
        "labelbox_metadata",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="index")
    frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="frameId"
    )
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    labelbox_data_row_id = sgqlc.types.Field(String, graphql_name="labelboxDataRowId")
    file_size = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="fileSize")
    frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameIndex"
    )
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    height = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="height")
    width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="width")
    preview_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="previewUrl"
    )
    preview_height = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewHeight"
    )
    preview_width = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewWidth"
    )
    preview_file_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="previewFileSize"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )
    next = sgqlc.types.Field(GraphqlID, graphql_name="next")
    next5 = sgqlc.types.Field(GraphqlID, graphql_name="next5")
    next100 = sgqlc.types.Field(GraphqlID, graphql_name="next100")
    next_flag = sgqlc.types.Field(GraphqlID, graphql_name="nextFlag")
    previous = sgqlc.types.Field(GraphqlID, graphql_name="previous")
    previous5 = sgqlc.types.Field(GraphqlID, graphql_name="previous5")
    previous100 = sgqlc.types.Field(GraphqlID, graphql_name="previous100")
    prev_flag = sgqlc.types.Field(GraphqlID, graphql_name="prevFlag")
    video = sgqlc.types.Field("Video", graphql_name="video")
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(DatasetAnnotation))
        ),
        graphql_name="annotations",
    )
    is_flagged = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFlagged"
    )
    is_empty = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEmpty")
    is_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isCoverImage"
    )
    annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotationCount"
    )
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    prediction_label_data = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("labelCount")),
        graphql_name="predictionLabelData",
    )
    annotation_label_data = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("labelCount")),
        graphql_name="annotationLabelData",
    )
    human_annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="humanAnnotationCount"
    )
    machine_annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="machineAnnotationCount"
    )
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    preview_md5 = sgqlc.types.Field(String, graphql_name="previewMd5")
    analytics_md5 = sgqlc.types.Field(String, graphql_name="analyticsMd5")
    analytics_file_size = sgqlc.types.Field(Float, graphql_name="analyticsFileSize")
    location = sgqlc.types.Field(String, graphql_name="location")
    description = sgqlc.types.Field(String, graphql_name="description")
    spectrum = sgqlc.types.Field(String, graphql_name="spectrum")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    dataset_frame_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="datasetFrameName"
    )
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(Attribute), graphql_name="attributes"
    )
    dataset_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="datasetName"
    )
    associated_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(AssociatedFrame)),
        graphql_name="associatedFrames",
    )
    labelbox_metadata = sgqlc.types.Field(String, graphql_name="labelboxMetadata")


class DatasetFrameCount(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("count",)
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class DatasetFrameOnly(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "owner",
        "frame_id",
        "video_id",
        "labelbox_data_row_id",
        "file_size",
        "frame_index",
        "url",
        "height",
        "width",
        "preview_url",
        "preview_height",
        "preview_width",
        "preview_file_size",
        "created_at",
        "modified_at",
        "annotations",
        "is_flagged",
        "is_empty",
        "annotation_count",
        "human_annotation_count",
        "machine_annotation_count",
        "is_cover_image",
        "is_favorite",
        "qa_status",
        "qa_status_note",
        "md5",
        "preview_md5",
        "analytics_md5",
        "analytics_file_size",
        "dataset_frame_name",
        "attributes",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    frame_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="frameId"
    )
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    labelbox_data_row_id = sgqlc.types.Field(
        GraphqlID, graphql_name="labelboxDataRowId"
    )
    file_size = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="fileSize")
    frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameIndex"
    )
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    height = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="height")
    width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="width")
    preview_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="previewUrl"
    )
    preview_height = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewHeight"
    )
    preview_width = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewWidth"
    )
    preview_file_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="previewFileSize"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(DatasetAnnotation))
        ),
        graphql_name="annotations",
    )
    is_flagged = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFlagged"
    )
    is_empty = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEmpty")
    annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotationCount"
    )
    human_annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="humanAnnotationCount"
    )
    machine_annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="machineAnnotationCount"
    )
    is_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isCoverImage"
    )
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    preview_md5 = sgqlc.types.Field(String, graphql_name="previewMd5")
    analytics_md5 = sgqlc.types.Field(String, graphql_name="analyticsMd5")
    analytics_file_size = sgqlc.types.Field(Float, graphql_name="analyticsFileSize")
    dataset_frame_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="datasetFrameName"
    )
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(Attribute), graphql_name="attributes"
    )


class DatasetFrames(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("dataset_frames", "total_count")
    dataset_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="datasetFrames",
    )
    total_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="totalCount"
    )


class DatasetFramesOnly(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("dataset_frames", "total_count")
    dataset_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrameOnly)),
        graphql_name="datasetFrames",
    )
    total_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="totalCount"
    )


class DatasetVideo(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("_id", "filename")
    _id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="_id")
    filename = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="filename")


class DatasetVideoSegment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "segment_length",
        "segment_frame_count",
        "segment_annotation_count",
        "segment_annotated_frame_count",
        "segment_flagged_frame_count",
    )
    segment_length = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="segmentLength"
    )
    segment_frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="segmentFrameCount"
    )
    segment_annotation_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="segmentAnnotationCount"
    )
    segment_annotated_frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="segmentAnnotatedFrameCount"
    )
    segment_flagged_frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="segmentFlaggedFrameCount"
    )


class DatasetVideoStatsResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("results", "count")
    results = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("VideoStats")), graphql_name="results"
    )
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class DatasheetJob(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "dataset_id",
        "git_commit",
        "state",
        "message",
        "created_by",
        "created_by_name",
        "created_at",
        "file_key",
        "signed_url",
        "modified_at",
        "config_data",
        "received_at",
        "processing_time",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    git_commit = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="gitCommit"
    )
    state = sgqlc.types.Field(
        sgqlc.types.non_null(DatasheetJobState), graphql_name="state"
    )
    message = sgqlc.types.Field(String, graphql_name="message")
    created_by = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="createdBy"
    )
    created_by_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="createdByName"
    )
    created_at = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name="createdAt")
    file_key = sgqlc.types.Field(String, graphql_name="fileKey")
    signed_url = sgqlc.types.Field(String, graphql_name="signedUrl")
    modified_at = sgqlc.types.Field(Date, graphql_name="modifiedAt")
    config_data = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="configData"
    )
    received_at = sgqlc.types.Field(Date, graphql_name="receivedAt")
    processing_time = sgqlc.types.Field(Float, graphql_name="processingTime")


class Domain(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("_id", "domain", "default_group")
    _id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="_id")
    domain = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="domain")
    default_group = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="defaultGroup"
    )


class Domains(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("domains", "count")
    domains = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Domain)), graphql_name="domains"
    )
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class ErrorArg(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("key", "value")
    key = sgqlc.types.Field(String, graphql_name="key")
    value = sgqlc.types.Field(String, graphql_name="value")


class Favorite(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "created_at",
        "user_id",
        "asset_id",
        "asset_type",
        "asset_name",
        "asset_location",
        "asset_display_url",
        "modified_at",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    user_id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="userId")
    asset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="assetId"
    )
    asset_type = sgqlc.types.Field(
        sgqlc.types.non_null(FavoriteAssetType), graphql_name="assetType"
    )
    asset_name = sgqlc.types.Field(String, graphql_name="assetName")
    asset_location = sgqlc.types.Field(String, graphql_name="assetLocation")
    asset_display_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="assetDisplayUrl"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )


class Frame(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "index",
        "video_id",
        "video_name",
        "url",
        "height",
        "width",
        "preview_url",
        "preview_height",
        "preview_width",
        "frame_index",
        "annotations",
        "annotations_count",
        "machine_annotations_count",
        "created_at",
        "modified_at",
        "owner",
        "cursor",
        "is_empty",
        "qa_status",
        "qa_status_note",
        "is_cover_image",
        "custom_metadata",
        "is_favorite",
        "favorite_count",
        "description",
        "tags",
        "spectrum",
        "location",
        "prediction_label_data",
        "annotation_label_data",
        "md5",
        "preview_md5",
        "analytics_md5",
        "attributes",
        "is_flagged",
        "dataset_frames",
        "is_key_frame",
        "associated_frames",
        "labelbox_metadata",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="index")
    video_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="videoId"
    )
    video_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="videoName"
    )
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    height = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="height")
    width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="width")
    preview_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="previewUrl"
    )
    preview_height = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewHeight"
    )
    preview_width = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="previewWidth"
    )
    frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameIndex"
    )
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Annotation))),
        graphql_name="annotations",
        args=sgqlc.types.ArgDict(
            (("id", sgqlc.types.Arg(GraphqlID, graphql_name="id", default=None)),)
        ),
    )
    annotations_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="annotationsCount"
    )
    machine_annotations_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="machineAnnotationsCount"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="cursor")
    is_empty = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEmpty")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    is_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isCoverImage"
    )
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    spectrum = sgqlc.types.Field(String, graphql_name="spectrum")
    location = sgqlc.types.Field(String, graphql_name="location")
    prediction_label_data = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("labelCount")),
        graphql_name="predictionLabelData",
    )
    annotation_label_data = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("labelCount")),
        graphql_name="annotationLabelData",
    )
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    preview_md5 = sgqlc.types.Field(String, graphql_name="previewMd5")
    analytics_md5 = sgqlc.types.Field(String, graphql_name="analyticsMd5")
    attributes = sgqlc.types.Field(
        sgqlc.types.list_of(Attribute), graphql_name="attributes"
    )
    is_flagged = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFlagged"
    )
    dataset_frames = sgqlc.types.Field(
        sgqlc.types.list_of(DatasetFrame), graphql_name="datasetFrames"
    )
    is_key_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isKeyFrame"
    )
    associated_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(AssociatedFrame)),
        graphql_name="associatedFrames",
    )
    labelbox_metadata = sgqlc.types.Field(String, graphql_name="labelboxMetadata")


class Frames(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("frames", "total_count", "cursor")
    frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Frame))),
        graphql_name="frames",
    )
    total_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="totalCount"
    )
    cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="cursor")


class GitCommit(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "_id",
        "author_name",
        "author_email",
        "size",
        "raw_message",
        "short_message",
        "commit_date",
        "tree",
        "parents",
    )
    _id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="_id")
    author_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="authorName"
    )
    author_email = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="authorEmail"
    )
    size = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="size")
    raw_message = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="rawMessage"
    )
    short_message = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="shortMessage"
    )
    commit_date = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="commitDate"
    )
    tree = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="tree")
    parents = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="parents")


class GitDiff(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "old_file_name",
        "old_header",
        "new_file_name",
        "new_header",
        "hunks",
    )
    old_file_name = sgqlc.types.Field(String, graphql_name="oldFileName")
    old_header = sgqlc.types.Field(String, graphql_name="oldHeader")
    new_file_name = sgqlc.types.Field(String, graphql_name="newFileName")
    new_header = sgqlc.types.Field(String, graphql_name="newHeader")
    hunks = sgqlc.types.Field(sgqlc.types.list_of("HUNK"), graphql_name="hunks")


class GitTree(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("_id", "dataset_id", "size", "tree_list")
    _id = sgqlc.types.Field(String, graphql_name="_id")
    dataset_id = sgqlc.types.Field(GraphqlID, graphql_name="datasetId")
    size = sgqlc.types.Field(Int, graphql_name="size")
    tree_list = sgqlc.types.Field(
        sgqlc.types.list_of("GitTreeItem"), graphql_name="treeList"
    )


class GitTreeItem(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("name", "mode", "size", "type", "_id")
    name = sgqlc.types.Field(String, graphql_name="name")
    mode = sgqlc.types.Field(Int, graphql_name="mode")
    size = sgqlc.types.Field(Int, graphql_name="size")
    type = sgqlc.types.Field(String, graphql_name="type")
    _id = sgqlc.types.Field(String, graphql_name="_id")


class Group(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "name",
        "members",
        "acl",
        "is_immutable",
        "notes",
        "conservator_insights_license_key",
        "group_type",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    members = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("User"))),
        graphql_name="members",
    )
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    is_immutable = sgqlc.types.Field(Boolean, graphql_name="isImmutable")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    conservator_insights_license_key = sgqlc.types.Field(
        String, graphql_name="conservatorInsightsLicenseKey"
    )
    group_type = sgqlc.types.Field(
        sgqlc.types.non_null(GroupType), graphql_name="groupType"
    )


class HUNK(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "old_start",
        "old_lines",
        "new_start",
        "new_lines",
        "lines",
        "linedelimiters",
    )
    old_start = sgqlc.types.Field(Int, graphql_name="oldStart")
    old_lines = sgqlc.types.Field(Int, graphql_name="oldLines")
    new_start = sgqlc.types.Field(Int, graphql_name="newStart")
    new_lines = sgqlc.types.Field(Int, graphql_name="newLines")
    lines = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name="lines")
    linedelimiters = sgqlc.types.Field(
        sgqlc.types.list_of(String), graphql_name="linedelimiters"
    )


class HumanAnnotationStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("total",)
    total = sgqlc.types.Field(Int, graphql_name="total")


class Image(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "filename",
        "url",
        "thumbnail_url",
        "preview_video_url",
        "md5",
        "cover_image_url",
        "state",
        "object_detect_state",
        "object_detect_error",
        "metadata",
        "created_at",
        "modified_at",
        "user_id",
        "user_id_name",
        "user_id_email",
        "uploaded_by",
        "uploaded_by_name",
        "uploaded_by_email",
        "frames",
        "frames_count",
        "annotations_count",
        "human_annotations_count",
        "name",
        "is_favorite",
        "favorite_count",
        "description",
        "location",
        "width",
        "height",
        "tags",
        "filmed_at",
        "raw_exif",
        "file_locker_files",
        "annotation_import_state",
        "annotation_import_state_modified_at",
        "process_video_error_message",
        "annotation_import_error_message",
        "highest_target_id",
        "custom_metadata",
        "collections",
        "datasets",
        "acl",
        "shared_with",
        "file_size",
        "object_detect_batches_total",
        "object_detect_batches_done",
        "spectrum",
        "asset_type",
        "object_detect_details",
        "inherited_acl",
        "readme",
        "image_md5",
        "image_preview_md5",
        "image_analytics_md5",
        "owner",
        "has_write_access",
        "has_admin_access",
        "processed_with_agc",
        "qa_status",
        "qa_status_note",
        "attached_label_set_ids",
        "attached_label_sets",
        "allow_annotations_outside_frame",
        "allow_duplicate_target_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    filename = sgqlc.types.Field(String, graphql_name="filename")
    url = sgqlc.types.Field(String, graphql_name="url")
    thumbnail_url = sgqlc.types.Field(String, graphql_name="thumbnailUrl")
    preview_video_url = sgqlc.types.Field(String, graphql_name="previewVideoUrl")
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    cover_image_url = sgqlc.types.Field(String, graphql_name="coverImageUrl")
    state = sgqlc.types.Field(VideoState, graphql_name="state")
    object_detect_state = sgqlc.types.Field(String, graphql_name="objectDetectState")
    object_detect_error = sgqlc.types.Field(String, graphql_name="objectDetectError")
    metadata = sgqlc.types.Field(String, graphql_name="metadata")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Float, graphql_name="modifiedAt")
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    user_id_name = sgqlc.types.Field(String, graphql_name="userIdName")
    user_id_email = sgqlc.types.Field(String, graphql_name="userIdEmail")
    uploaded_by = sgqlc.types.Field(String, graphql_name="uploadedBy")
    uploaded_by_name = sgqlc.types.Field(String, graphql_name="uploadedByName")
    uploaded_by_email = sgqlc.types.Field(String, graphql_name="uploadedByEmail")
    frames = sgqlc.types.Field(
        sgqlc.types.list_of(Frame),
        graphql_name="frames",
        args=sgqlc.types.ArgDict(
            (
                ("id", sgqlc.types.Arg(GraphqlID, graphql_name="id", default=None)),
                (
                    "frame_index",
                    sgqlc.types.Arg(Int, graphql_name="frameIndex", default=None),
                ),
                (
                    "start_frame_index",
                    sgqlc.types.Arg(Int, graphql_name="startFrameIndex", default=None),
                ),
                (
                    "custom_metadata",
                    sgqlc.types.Arg(
                        String, graphql_name="customMetadata", default=None
                    ),
                ),
            )
        ),
    )
    frames_count = sgqlc.types.Field(Int, graphql_name="framesCount")
    annotations_count = sgqlc.types.Field(Int, graphql_name="annotationsCount")
    human_annotations_count = sgqlc.types.Field(
        Int, graphql_name="humanAnnotationsCount"
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    location = sgqlc.types.Field(String, graphql_name="location")
    width = sgqlc.types.Field(Int, graphql_name="width")
    height = sgqlc.types.Field(Int, graphql_name="height")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    filmed_at = sgqlc.types.Field(Date, graphql_name="filmedAt")
    raw_exif = sgqlc.types.Field(String, graphql_name="rawExif")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of("file"), graphql_name="fileLockerFiles"
    )
    annotation_import_state = sgqlc.types.Field(
        AnnotationImportState, graphql_name="annotationImportState"
    )
    annotation_import_state_modified_at = sgqlc.types.Field(
        Date, graphql_name="annotationImportStateModifiedAt"
    )
    process_video_error_message = sgqlc.types.Field(
        String, graphql_name="processVideoErrorMessage"
    )
    annotation_import_error_message = sgqlc.types.Field(
        String, graphql_name="annotationImportErrorMessage"
    )
    highest_target_id = sgqlc.types.Field(Int, graphql_name="highestTargetId")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    collections = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))),
        graphql_name="collections",
    )
    datasets = sgqlc.types.Field(sgqlc.types.list_of(Dataset), graphql_name="datasets")
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    shared_with = sgqlc.types.Field(AclPermissionLevels, graphql_name="sharedWith")
    file_size = sgqlc.types.Field(Float, graphql_name="fileSize")
    object_detect_batches_total = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesTotal"
    )
    object_detect_batches_done = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesDone"
    )
    spectrum = sgqlc.types.Field(String, graphql_name="spectrum")
    asset_type = sgqlc.types.Field(String, graphql_name="assetType")
    object_detect_details = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("ObjectDetectDetails")),
        graphql_name="objectDetectDetails",
    )
    inherited_acl = sgqlc.types.Field(Acl, graphql_name="inheritedAcl")
    readme = sgqlc.types.Field(String, graphql_name="readme")
    image_md5 = sgqlc.types.Field(String, graphql_name="imageMd5")
    image_preview_md5 = sgqlc.types.Field(String, graphql_name="imagePreviewMd5")
    image_analytics_md5 = sgqlc.types.Field(String, graphql_name="imageAnalyticsMd5")
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    has_write_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasWriteAccess"
    )
    has_admin_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasAdminAccess"
    )
    processed_with_agc = sgqlc.types.Field(String, graphql_name="processedWithAGC")
    qa_status = sgqlc.types.Field(String, graphql_name="qaStatus")
    qa_status_note = sgqlc.types.Field(String, graphql_name="qaStatusNote")
    attached_label_set_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="attachedLabelSetIds"
    )
    attached_label_sets = sgqlc.types.Field(
        sgqlc.types.list_of("LabelSet"), graphql_name="attachedLabelSets"
    )
    allow_annotations_outside_frame = sgqlc.types.Field(
        Boolean, graphql_name="allowAnnotationsOutsideFrame"
    )
    allow_duplicate_target_id = sgqlc.types.Field(
        Boolean, graphql_name="allowDuplicateTargetId"
    )


class InterpolationResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("annotations_created", "error_frame", "error_target_id")
    annotations_created = sgqlc.types.Field(Int, graphql_name="annotationsCreated")
    error_frame = sgqlc.types.Field(Int, graphql_name="errorFrame")
    error_target_id = sgqlc.types.Field(Int, graphql_name="errorTargetId")


class Label(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "name",
        "label_set_id",
        "color",
        "is_removed",
        "attribute_prototypes",
        "tool",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedLabelCharacters), graphql_name="name"
    )
    label_set_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="labelSetId"
    )
    color = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="color")
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")
    attribute_prototypes = sgqlc.types.Field(
        sgqlc.types.list_of(AttributePrototype), graphql_name="attributePrototypes"
    )
    tool = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="tool")


class LabelSet(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "name",
        "created_at",
        "modified_at",
        "is_removed",
        "labels",
        "acl",
        "attribute_prototypes",
        "notes",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    created_at = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Date, graphql_name="modifiedAt")
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Label)), graphql_name="labels"
    )
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    attribute_prototypes = sgqlc.types.Field(
        sgqlc.types.list_of(AttributePrototype), graphql_name="attributePrototypes"
    )
    notes = sgqlc.types.Field(String, graphql_name="notes")


class MachineAnnotationStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("total",)
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class Md5Asset(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("md5", "dataset_details", "video_details")
    md5 = sgqlc.types.Field(sgqlc.types.non_null(Md5String), graphql_name="md5")
    dataset_details = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Md5DatasetDetails")),
        graphql_name="datasetDetails",
    )
    video_details = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Md5VideoDetails")),
        graphql_name="videoDetails",
    )


class Md5DatasetDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("dataset", "dataset_frame")
    dataset = sgqlc.types.Field(Dataset, graphql_name="dataset")
    dataset_frame = sgqlc.types.Field(DatasetFrame, graphql_name="datasetFrame")


class Md5Result(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("md5", "exists")
    md5 = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="md5")
    exists = sgqlc.types.Field(sgqlc.types.non_null(Md5Exists), graphql_name="exists")


class Md5VideoDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("video", "frame")
    video = sgqlc.types.Field("Video", graphql_name="video")
    frame = sgqlc.types.Field(Frame, graphql_name="frame")


class Mutation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "generate_signed_metadata_upload_url",
        "mark_annotation_as_uploaded",
        "create_annotations",
        "create_prediction",
        "update_annotation",
        "remove_annotations",
        "accept_annotations",
        "move_annotations",
        "approve_annotation",
        "request_changes_annotation",
        "unset_qa_status_annotation",
        "update_qa_status_note_annotation",
        "sign_in",
        "sign_out",
        "create_collection",
        "update_collection",
        "delete_collection",
        "update_collection_acl",
        "remove_collection_acl",
        "generate_signed_collection_file_locker_upload_url",
        "remove_collection_file_locker_file",
        "recalculate_collection_stats",
        "move_collection",
        "commit_dataset",
        "create_dataset",
        "update_dataset",
        "delete_dataset",
        "archive_dataset",
        "add_segments_to_dataset",
        "add_videos_to_dataset",
        "add_frames_to_dataset",
        "remove_frames_from_dataset",
        "remove_frames_from_dataset_by_ids",
        "create_dataset_by_frame_filter",
        "update_dataset_acl",
        "add_dataset_acl",
        "remove_dataset_acl",
        "update_dataset_cover_image",
        "merge_datasets",
        "annotate_dataset_using_machine_learning",
        "generate_signed_dataset_metadata_upload_url",
        "mark_dataset_annotation_as_uploaded",
        "dataset_labelbox_export",
        "dataset_labelbox_import",
        "dataset_labelbox_sync",
        "dataset_labelbox_remove",
        "generate_signed_dataset_file_locker_upload_url",
        "remove_dataset_file_locker_file",
        "copy_dataset_annotations_to_video",
        "generate_dataset_metadata",
        "update_dataset_custom_metadata",
        "delete_all_dataset_annotations",
        "delete_all_dataset_predictions",
        "copy_dataset_to_dataset",
        "restore_dataset",
        "commit_all_collection_datasets",
        "generate_dataset_preview_video",
        "move_dataset",
        "recalculate_dataset_stats",
        "create_dataset_annotations",
        "accept_dataset_annotations",
        "update_dataset_annotation",
        "delete_dataset_annotations",
        "move_dataset_annotations",
        "approve_dataset_annotation",
        "request_changes_dataset_annotation",
        "unset_qa_status_dataset_annotation",
        "update_qa_status_note_dataset_annotation",
        "flag_dataset_frame",
        "unflag_dataset_frame",
        "mark_dataset_frame_empty",
        "unmark_dataset_frame_empty",
        "approve_dataset_frame",
        "request_changes_dataset_frame",
        "unset_qa_status_dataset_frame",
        "update_dataset_qa_status_note",
        "update_dataset_frame",
        "add_dataset_frame_attribute",
        "remove_dataset_frame_attribute",
        "modify_dataset_frame_attribute",
        "add_dataset_annotation_attribute",
        "remove_dataset_annotation_attribute",
        "modify_dataset_annotation_attribute",
        "copy_dataset_annotations",
        "delete_dataset_frames_by_search",
        "add_associated_frame_to_dataset_frame",
        "remove_associated_frame_from_dataset_frame",
        "dataset_frame_id_from_index",
        "copy_filtered_frames_to_dataset",
        "copy_frames_to_dataset",
        "remove_dataset_frame_predictions",
        "create_dataset_frames",
        "create_datasheet",
        "update_datasheet_job_state",
        "complete_datasheet_job_success",
        "complete_datasheet_job_fail",
        "mark_frame_empty",
        "unmark_frame_empty",
        "set_key_frame",
        "mark_frames_empty",
        "unmark_frames_empty",
        "add_frame",
        "update_frame",
        "approve_frame",
        "request_changes_frame",
        "unset_qa_status_frame",
        "update_qa_status_note",
        "add_video_frame_attribute",
        "remove_video_frame_attribute",
        "modify_video_frame_attribute",
        "add_video_annotation_attribute",
        "remove_video_annotation_attribute",
        "modify_video_annotation_attribute",
        "flag_frame",
        "unflag_frame",
        "copy_video_annotations",
        "interpolate_video_annotations",
        "add_associated_frame_to_frame",
        "remove_associated_frame_from_frame",
        "remove_frame_predictions",
        "create_group",
        "clone_group",
        "update_group",
        "delete_group",
        "add_group_members",
        "remove_group_members",
        "update_group_acl",
        "add_group_acl",
        "remove_group_acl",
        "update_group_note",
        "create_label_set",
        "remove_label_set",
        "update_label_set",
        "update_labelset_note",
        "add_label_set_attribute_prototype",
        "remove_label_set_attribute_prototype",
        "modify_label_set_attribute_prototype",
        "clone_labelset",
        "generate_signed_labelset_upload_url",
        "mark_label_set_as_uploaded",
        "create_label",
        "remove_label",
        "update_label",
        "add_label_attribute_prototype",
        "remove_label_attribute_prototype",
        "modify_label_attribute_prototype",
        "create_segment",
        "update_segment",
        "delete_segment",
        "generate_api_key",
        "delete_api_key",
        "update_user_role",
        "delete_users",
        "update_user",
        "create_user",
        "set_local_password",
        "reset_local_password",
        "remove_user_labelbox_api_key",
        "sign_in_lock",
        "sign_in_un_lock",
        "update_user_note",
        "refresh_user_data",
        "insert_favorite",
        "remove_favorite",
        "create_video",
        "initiate_video_upload",
        "generate_signed_video_upload_url",
        "generate_signed_file_locker_upload_url",
        "generate_signed_multipart_video_upload_url",
        "complete_video_upload",
        "abort_video_upload",
        "remove_file_locker_file",
        "annotate_videos_using_machine_learning",
        "update_video",
        "remove_video",
        "restore_video",
        "process_video",
        "process_videos",
        "update_video_acl",
        "add_video_acl",
        "remove_video_acl",
        "update_video_cover_image",
        "unset_video_cover_image",
        "update_video_custom_metadata",
        "copy_annotations_to_dataset",
        "video_labelbox_export",
        "video_labelbox_import",
        "video_labelbox_remove",
        "video_labelbox_update",
        "delete_all_video_annotations",
        "delete_all_video_predictions",
        "generate_full_res_video",
        "generate_annotated_preview",
        "set_videos_admin_failed",
        "create_video_full",
        "move_video",
        "recalculate_video_stats",
        "add_domain",
        "update_domain",
        "remove_domain",
        "create_saved_search",
        "delete_saved_search",
        "update_saved_search",
        "share_saved_search",
        "update_commit_version_note",
        "create_project",
        "update_project",
        "delete_project",
        "update_project_acl",
        "remove_project_acl",
        "create_collection_sqarun",
        "update_collection_sqarun_status",
        "complete_sqarun_success",
        "complete_sqarun_fail",
    )
    generate_signed_metadata_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedMetadataUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_annotation_as_uploaded = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="markAnnotationAsUploaded",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "url",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="url", default=None
                    ),
                ),
                (
                    "create_missing_frames",
                    sgqlc.types.Arg(
                        Boolean, graphql_name="createMissingFrames", default=None
                    ),
                ),
            )
        ),
    )
    create_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Annotation))),
        graphql_name="createAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "annotations",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(AnnotationCreate))
                        ),
                        graphql_name="annotations",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_prediction = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="createPrediction",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "prediction",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(PredictionCreate),
                        graphql_name="prediction",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="updateAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "annotation",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AnnotationUpdate),
                        graphql_name="annotation",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="removeAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveAnnotationsInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    accept_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Annotation)),
        graphql_name="acceptAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "annotations",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(AcceptAnnotation)),
                        graphql_name="annotations",
                        default=None,
                    ),
                ),
            )
        ),
    )
    move_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Annotation))),
        graphql_name="moveAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MoveAnnotationsInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    approve_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="approveAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    request_changes_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="requestChangesAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    unset_qa_status_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="unsetQaStatusAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_qa_status_note_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(Annotation),
        graphql_name="updateQaStatusNoteAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateQaStatusNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    sign_in = sgqlc.types.Field(
        sgqlc.types.non_null(AuthPayload),
        graphql_name="signIn",
        args=sgqlc.types.ArgDict(
            (
                (
                    "email",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="email", default=None
                    ),
                ),
                (
                    "password",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="password",
                        default=None,
                    ),
                ),
            )
        ),
    )
    sign_out = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="signOut",
        args=sgqlc.types.ArgDict(
            (
                (
                    "session_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="sessionId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_collection = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="createCollection",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CreateCollectionInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_collection = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="updateCollection",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateCollectionInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_collection = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="deleteCollection",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DeleteCollectionInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_collection_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="updateCollectionAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_collection_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="removeCollectionAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_collection_file_locker_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedCollectionFileLockerUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_collection_file_locker_file = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="removeCollectionFileLockerFile",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionId",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    recalculate_collection_stats = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="recalculateCollectionStats",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    move_collection = sgqlc.types.Field(
        sgqlc.types.non_null(Collection),
        graphql_name="moveCollection",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "parent_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="parentId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    commit_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID),
        graphql_name="commitDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "commit_message",
                    sgqlc.types.Arg(String, graphql_name="commitMessage", default=None),
                ),
                (
                    "user_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="userId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="createDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CreateDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="updateDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="deleteDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DeleteDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    archive_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="archiveDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ArchiveDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_segments_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="addSegmentsToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddSegmentsToDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_videos_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="addVideosToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddVideosToDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_frames_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="addFramesToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddFramesToDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_frames_from_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="removeFramesFromDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveFramesFromDatasetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_frames_from_dataset_by_ids = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="removeFramesFromDatasetByIds",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveFramesFromDatasetByIdsInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_dataset_by_frame_filter = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="createDatasetByFrameFilter",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(StringLowerCase),
                        graphql_name="name",
                        default=None,
                    ),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FrameFilter),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="updateDatasetAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_dataset_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="addDatasetAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_dataset_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="removeDatasetAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="updateDatasetCoverImage",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    merge_datasets = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="mergeDatasets",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        MergeDatasetInput, graphql_name="input", default=None
                    ),
                ),
            )
        ),
    )
    annotate_dataset_using_machine_learning = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="annotateDatasetUsingMachineLearning",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "classifier_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="classifierId",
                        default=None,
                    ),
                ),
                (
                    "frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(GraphqlID),
                        graphql_name="frameIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_dataset_metadata_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedDatasetMetadataUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_dataset_annotation_as_uploaded = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="markDatasetAnnotationAsUploaded",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "url",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="url", default=None
                    ),
                ),
                (
                    "commit_msg",
                    sgqlc.types.Arg(String, graphql_name="commitMsg", default=None),
                ),
            )
        ),
    )
    dataset_labelbox_export = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="datasetLabelboxExport",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "frontend_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="frontendId",
                        default=None,
                    ),
                ),
                (
                    "label_set",
                    sgqlc.types.Arg(GraphqlID, graphql_name="labelSet", default=None),
                ),
            )
        ),
    )
    dataset_labelbox_import = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="datasetLabelboxImport",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    dataset_labelbox_sync = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="datasetLabelboxSync",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    dataset_labelbox_remove = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="datasetLabelboxRemove",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_dataset_file_locker_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedDatasetFileLockerUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_dataset_file_locker_file = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="removeDatasetFileLockerFile",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    copy_dataset_annotations_to_video = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="copyDatasetAnnotationsToVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_dataset_metadata = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="generateDatasetMetadata",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset_custom_metadata = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="updateDatasetCustomMetadata",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "custom_metadata",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="customMetadata",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_all_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="deleteAllDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_all_dataset_predictions = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="deleteAllDatasetPredictions",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    copy_dataset_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="copyDatasetToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "source_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceDatasetId",
                        default=None,
                    ),
                ),
                (
                    "target_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="targetDatasetId",
                        default=None,
                    ),
                ),
                (
                    "duplicate_action",
                    sgqlc.types.Arg(
                        DuplicateAction, graphql_name="duplicateAction", default=None
                    ),
                ),
            )
        ),
    )
    restore_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Dataset),
        graphql_name="restoreDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    commit_all_collection_datasets = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="commitAllCollectionDatasets",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionId",
                        default=None,
                    ),
                ),
                (
                    "commit_message",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="commitMessage",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_dataset_preview_video = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="generateDatasetPreviewVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    move_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="moveDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MoveAssetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    recalculate_dataset_stats = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="recalculateDatasetStats",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(DatasetAnnotation))
        ),
        graphql_name="createDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(
                                sgqlc.types.non_null(CreateDatasetAnnotationInput)
                            )
                        ),
                        graphql_name="input",
                        default=None,
                    ),
                ),
                (
                    "skip_stats",
                    sgqlc.types.Arg(Boolean, graphql_name="skipStats", default=None),
                ),
            )
        ),
    )
    accept_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetAnnotation)),
        graphql_name="acceptDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "annotations",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(AcceptDatasetAnnotationInput)
                        ),
                        graphql_name="annotations",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetAnnotation),
        graphql_name="updateDatasetAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateDatasetAnnotationInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetAnnotation)),
        graphql_name="deleteDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DeleteDatasetAnnotationsInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    move_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(DatasetAnnotation))
        ),
        graphql_name="moveDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MoveAnnotationsInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    approve_dataset_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetAnnotation),
        graphql_name="approveDatasetAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    request_changes_dataset_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetAnnotation),
        graphql_name="requestChangesDatasetAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "frame_qastatus",
                    sgqlc.types.Arg(String, graphql_name="frameQAStatus", default=None),
                ),
            )
        ),
    )
    unset_qa_status_dataset_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetAnnotation),
        graphql_name="unsetQaStatusDatasetAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_qa_status_note_dataset_annotation = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetAnnotation),
        graphql_name="updateQaStatusNoteDatasetAnnotation",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "qa_status_note",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="qaStatusNote",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    flag_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="flagDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FlagDatasetFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unflag_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="unflagDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UnflagDatasetFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_dataset_frame_empty = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="markDatasetFrameEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    unmark_dataset_frame_empty = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="unmarkDatasetFrameEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    approve_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="approveDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    request_changes_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="requestChangesDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    unset_qa_status_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="unsetQaStatusDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_dataset_qa_status_note = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="updateDatasetQaStatusNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateDatasetQaStatusNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="updateDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "metadata",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DatasetFrameMetadataInput),
                        graphql_name="metadata",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_dataset_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="addDatasetFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_dataset_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="removeDatasetFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_dataset_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="modifyDatasetFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_dataset_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="addDatasetAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_dataset_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="removeDatasetAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_dataset_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="modifyDatasetAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    copy_dataset_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(CopyDatasetAnnotationsResponse),
        graphql_name="copyDatasetAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "source_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceFrameId",
                        default=None,
                    ),
                ),
                (
                    "destination_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="destinationFrameId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_dataset_frames_by_search = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="deleteDatasetFramesBySearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="searchText",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_associated_frame_to_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="addAssociatedFrameToDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAssociatedFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_associated_frame_from_dataset_frame = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrame),
        graphql_name="removeAssociatedFrameFromDatasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetFrameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveAssociatedFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    dataset_frame_id_from_index = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="datasetFrameIdFromIndex",
        args=sgqlc.types.ArgDict(
            (
                (
                    "index",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="index", default=None
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("sort", sgqlc.types.Arg(String, graphql_name="sort", default=None)),
            )
        ),
    )
    copy_filtered_frames_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="copyFilteredFramesToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "source_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceDatasetId",
                        default=None,
                    ),
                ),
                (
                    "target_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="targetDatasetId",
                        default=None,
                    ),
                ),
                (
                    "overwrite",
                    sgqlc.types.Arg(Boolean, graphql_name="overwrite", default=None),
                ),
            )
        ),
    )
    copy_frames_to_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="copyFramesToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "source_frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="sourceFrameIds",
                        default=None,
                    ),
                ),
                (
                    "source_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceDatasetId",
                        default=None,
                    ),
                ),
                (
                    "target_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="targetDatasetId",
                        default=None,
                    ),
                ),
                (
                    "overwrite",
                    sgqlc.types.Arg(Boolean, graphql_name="overwrite", default=None),
                ),
            )
        ),
    )
    remove_dataset_frame_predictions = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="removeDatasetFramePredictions",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "dataset_frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="datasetFrameIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_dataset_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="createDatasetFrames",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "dataset_frames",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(
                                sgqlc.types.non_null(CreateDatasetFrameInput)
                            )
                        ),
                        graphql_name="datasetFrames",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_datasheet = sgqlc.types.Field(
        sgqlc.types.non_null(DatasheetJob),
        graphql_name="createDatasheet",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "git_commit",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="gitCommit",
                        default=None,
                    ),
                ),
                (
                    "config_data",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="configData",
                        default=None,
                    ),
                ),
                (
                    "email_notification",
                    sgqlc.types.Arg(
                        Boolean, graphql_name="emailNotification", default=None
                    ),
                ),
            )
        ),
    )
    update_datasheet_job_state = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="updateDatasheetJobState",
        args=sgqlc.types.ArgDict(
            (
                (
                    "datasheet_job_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasheetJobId",
                        default=None,
                    ),
                ),
                (
                    "state",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DatasheetJobState),
                        graphql_name="state",
                        default=None,
                    ),
                ),
                (
                    "message",
                    sgqlc.types.Arg(String, graphql_name="message", default=None),
                ),
            )
        ),
    )
    complete_datasheet_job_success = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="completeDatasheetJobSuccess",
        args=sgqlc.types.ArgDict(
            (
                (
                    "datasheet_job_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasheetJobId",
                        default=None,
                    ),
                ),
                (
                    "file_key",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="fileKey",
                        default=None,
                    ),
                ),
            )
        ),
    )
    complete_datasheet_job_fail = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="completeDatasheetJobFail",
        args=sgqlc.types.ArgDict(
            (
                (
                    "datasheet_job_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasheetJobId",
                        default=None,
                    ),
                ),
                (
                    "message",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="message",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_frame_empty = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="markFrameEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    unmark_frame_empty = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="unmarkFrameEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    set_key_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="setKeyFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "key_frame",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Boolean),
                        graphql_name="keyFrame",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_frames_empty = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="markFramesEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unmark_frames_empty = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="unmarkFramesEmpty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="addFrame",
        args=sgqlc.types.ArgDict(
            (
                ("id", sgqlc.types.Arg(GraphqlID, graphql_name="id", default=None)),
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "frame_index",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int),
                        graphql_name="frameIndex",
                        default=None,
                    ),
                ),
                ("md5", sgqlc.types.Arg(String, graphql_name="md5", default=None)),
                (
                    "height",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="height", default=None
                    ),
                ),
                (
                    "width",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="width", default=None
                    ),
                ),
                (
                    "preview_md5",
                    sgqlc.types.Arg(String, graphql_name="previewMd5", default=None),
                ),
                (
                    "preview_height",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int),
                        graphql_name="previewHeight",
                        default=None,
                    ),
                ),
                (
                    "preview_width",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int),
                        graphql_name="previewWidth",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="updateFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "metadata",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FrameMetadataInput),
                        graphql_name="metadata",
                        default=None,
                    ),
                ),
            )
        ),
    )
    approve_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="approveFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    request_changes_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="requestChangesFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    unset_qa_status_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="unsetQaStatusFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_qa_status_note = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="updateQaStatusNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateQaStatusNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_video_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="addVideoFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_video_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="removeVideoFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_video_frame_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="modifyVideoFrameAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_video_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="addVideoAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_video_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="removeVideoAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_video_annotation_attribute = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="modifyVideoAnnotationAttribute",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "annotation_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="annotationId",
                        default=None,
                    ),
                ),
                (
                    "attribute_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    flag_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="flagFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unflag_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="unflagFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    copy_video_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(CopyVideoAnnotationsResponse),
        graphql_name="copyVideoAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "source_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceFrameId",
                        default=None,
                    ),
                ),
                (
                    "destination_frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="destinationFrameId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    interpolate_video_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(InterpolationResult),
        graphql_name="interpolateVideoAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(InterpolationInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_associated_frame_to_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="addAssociatedFrameToFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAssociatedFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_associated_frame_from_frame = sgqlc.types.Field(
        sgqlc.types.non_null(Frame),
        graphql_name="removeAssociatedFrameFromFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveAssociatedFrameInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_frame_predictions = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Frame)),
        graphql_name="removeFramePredictions",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="frameIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="createGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CreateGroupInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    clone_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="cloneGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "group_id_to_be_cloned",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="groupIdToBeCloned",
                        default=None,
                    ),
                ),
                (
                    "cloned_group_name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="clonedGroupName",
                        default=None,
                    ),
                ),
                (
                    "options",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CloneGroupOptions),
                        graphql_name="options",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="updateGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateGroupInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="deleteGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DeleteGroupInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_group_members = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="addGroupMembers",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddGroupMembersInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_group_members = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="removeGroupMembers",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RemoveGroupMembersInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_group_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="updateGroupAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_group_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="addGroupAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_group_acl = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="removeGroupAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_group_note = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="updateGroupNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateGroupNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_label_set = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="createLabelSet",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
            )
        ),
    )
    remove_label_set = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="removeLabelSet",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_label_set = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="updateLabelSet",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
            )
        ),
    )
    update_labelset_note = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="updateLabelsetNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateLabelsetNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_label_set_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="addLabelSetAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributePrototypeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_label_set_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="removeLabelSetAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "label_set_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="labelSetId",
                        default=None,
                    ),
                ),
                (
                    "attribute_prototype_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributePrototypeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_label_set_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="modifyLabelSetAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "label_set_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="labelSetId",
                        default=None,
                    ),
                ),
                (
                    "attribute_prototype_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributePrototypeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributePrototypeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    clone_labelset = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="cloneLabelset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
            )
        ),
    )
    generate_signed_labelset_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedLabelsetUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
            )
        ),
    )
    mark_label_set_as_uploaded = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="markLabelSetAsUploaded",
        args=sgqlc.types.ArgDict(
            (
                (
                    "url",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="url", default=None
                    ),
                ),
            )
        ),
    )
    create_label = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="createLabel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(LabelInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_label = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="removeLabel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_label = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="updateLabel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(LabelUpdate),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_label_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="addLabelAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AddAttributePrototypeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_label_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="removeLabelAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "label_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="labelId",
                        default=None,
                    ),
                ),
                (
                    "attribute_prototype_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributePrototypeId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    modify_label_attribute_prototype = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="modifyLabelAttributePrototype",
        args=sgqlc.types.ArgDict(
            (
                (
                    "label_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="labelId",
                        default=None,
                    ),
                ),
                (
                    "attribute_prototype_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="attributePrototypeId",
                        default=None,
                    ),
                ),
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ModifyAttributePrototypeInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_segment = sgqlc.types.Field(
        sgqlc.types.non_null("Segment"),
        graphql_name="createSegment",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CreateSegmentInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_segment = sgqlc.types.Field(
        sgqlc.types.non_null("Segment"),
        graphql_name="updateSegment",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateSegmentInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_segment = sgqlc.types.Field(
        sgqlc.types.non_null("Segment"),
        graphql_name="deleteSegment",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DeleteSegmentInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_api_key = sgqlc.types.Field(
        sgqlc.types.non_null("User"), graphql_name="generateApiKey"
    )
    delete_api_key = sgqlc.types.Field(
        sgqlc.types.non_null("User"), graphql_name="deleteApiKey"
    )
    update_user_role = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="updateUserRole",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "role",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="role", default=None
                    ),
                ),
            )
        ),
    )
    delete_users = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("User")),
        graphql_name="deleteUsers",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_user = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="updateUser",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("name", sgqlc.types.Arg(String, graphql_name="name", default=None)),
                ("role", sgqlc.types.Arg(String, graphql_name="role", default=None)),
                (
                    "groups_to_be_removed",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="groupsToBeRemoved",
                        default=None,
                    ),
                ),
                (
                    "labelbox_api_key",
                    sgqlc.types.Arg(
                        String, graphql_name="labelboxApiKey", default=None
                    ),
                ),
            )
        ),
    )
    create_user = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="createUser",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
                (
                    "email",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="email", default=None
                    ),
                ),
                (
                    "password",
                    sgqlc.types.Arg(String, graphql_name="password", default=None),
                ),
                (
                    "role",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="role", default=None
                    ),
                ),
                (
                    "groups",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="groups",
                        default=None,
                    ),
                ),
            )
        ),
    )
    set_local_password = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="setLocalPassword",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "password",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="password",
                        default=None,
                    ),
                ),
            )
        ),
    )
    reset_local_password = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="resetLocalPassword",
        args=sgqlc.types.ArgDict(
            (
                (
                    "new_password",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="newPassword",
                        default=None,
                    ),
                ),
                (
                    "old_password",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="oldPassword",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_user_labelbox_api_key = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="removeUserLabelboxApiKey",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    sign_in_lock = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("User")),
        graphql_name="signInLock",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    sign_in_un_lock = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("User")),
        graphql_name="signInUnLock",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_user_note = sgqlc.types.Field(
        sgqlc.types.non_null("User"),
        graphql_name="updateUserNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateUserNoteInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    refresh_user_data = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="refreshUserData",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    insert_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Favorite),
        graphql_name="insertFavorite",
        args=sgqlc.types.ArgDict(
            (
                (
                    "asset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="assetId",
                        default=None,
                    ),
                ),
                (
                    "asset_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FavoriteAssetType),
                        graphql_name="assetType",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="removeFavorite",
        args=sgqlc.types.ArgDict(
            (
                (
                    "asset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="assetId",
                        default=None,
                    ),
                ),
                (
                    "asset_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FavoriteAssetType),
                        graphql_name="assetType",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_video = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="createVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(GraphqlID, graphql_name="videoId", default=None),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
                (
                    "validate",
                    sgqlc.types.Arg(Boolean, graphql_name="validate", default=None),
                ),
            )
        ),
    )
    initiate_video_upload = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="initiateVideoUpload",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_video_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedVideoUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_file_locker_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null("SignedUrl"),
        graphql_name="generateSignedFileLockerUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "content_type",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="contentType",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_signed_multipart_video_upload_url = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="generateSignedMultipartVideoUploadUrl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "part_number",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int),
                        graphql_name="partNumber",
                        default=None,
                    ),
                ),
                (
                    "upload_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="uploadId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    complete_video_upload = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="completeVideoUpload",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
                (
                    "upload_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="uploadId",
                        default=None,
                    ),
                ),
                (
                    "completion_tags",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(sgqlc.types.non_null(String)),
                        graphql_name="completionTags",
                        default=None,
                    ),
                ),
            )
        ),
    )
    abort_video_upload = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="abortVideoUpload",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "upload_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="uploadId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_file_locker_file = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="removeFileLockerFile",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "filename",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="filename",
                        default=None,
                    ),
                ),
            )
        ),
    )
    annotate_videos_using_machine_learning = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="annotateVideosUsingMachineLearning",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
                (
                    "classifier_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="classifierId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_video = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="updateVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "metadata",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MetadataInput),
                        graphql_name="metadata",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_video = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="removeVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    restore_video = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="restoreVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    process_video = sgqlc.types.Field(
        "Video",
        graphql_name="processVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "should_notify",
                    sgqlc.types.Arg(Boolean, graphql_name="shouldNotify", default=None),
                ),
                (
                    "metadata_url",
                    sgqlc.types.Arg(String, graphql_name="metadataUrl", default=None),
                ),
                (
                    "should_object_detect",
                    sgqlc.types.Arg(
                        Boolean, graphql_name="shouldObjectDetect", default=None
                    ),
                ),
                (
                    "new_upload",
                    sgqlc.types.Arg(Boolean, graphql_name="newUpload", default=None),
                ),
            )
        ),
    )
    process_videos = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="processVideos",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
                (
                    "should_notify",
                    sgqlc.types.Arg(Boolean, graphql_name="shouldNotify", default=None),
                ),
                (
                    "classifier_id",
                    sgqlc.types.Arg(String, graphql_name="classifierId", default=None),
                ),
                ("agc", sgqlc.types.Arg(String, graphql_name="agc", default=None)),
            )
        ),
    )
    update_video_acl = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="updateVideoAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_video_acl = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="addVideoAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_video_acl = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="removeVideoAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_video_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="updateVideoCoverImage",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unset_video_cover_image = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="unsetVideoCoverImage",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_video_custom_metadata = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="updateVideoCustomMetadata",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "custom_metadata",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="customMetadata",
                        default=None,
                    ),
                ),
            )
        ),
    )
    copy_annotations_to_dataset = sgqlc.types.Field(
        Boolean,
        graphql_name="copyAnnotationsToDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    video_labelbox_export = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="videoLabelboxExport",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "frontend_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="frontendId",
                        default=None,
                    ),
                ),
                (
                    "label_set",
                    sgqlc.types.Arg(GraphqlID, graphql_name="labelSet", default=None),
                ),
            )
        ),
    )
    video_labelbox_import = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="videoLabelboxImport",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    video_labelbox_remove = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="videoLabelboxRemove",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    video_labelbox_update = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="videoLabelboxUpdate",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_all_video_annotations = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="deleteAllVideoAnnotations",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_all_video_predictions = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="deleteAllVideoPredictions",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_full_res_video = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="generateFullResVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    generate_annotated_preview = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="generateAnnotatedPreview",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    set_videos_admin_failed = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="setVideosAdminFailed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="videoIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_video_full = sgqlc.types.Field(
        sgqlc.types.non_null("Video"),
        graphql_name="createVideoFull",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FullVideoInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
                (
                    "validate",
                    sgqlc.types.Arg(Boolean, graphql_name="validate", default=None),
                ),
            )
        ),
    )
    move_video = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="moveVideo",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MoveAssetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    recalculate_video_stats = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="recalculateVideoStats",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_domain = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedDomain),
        graphql_name="addDomain",
        args=sgqlc.types.ArgDict(
            (
                (
                    "domain",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="domain",
                        default=None,
                    ),
                ),
                (
                    "default_group",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="defaultGroup",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_domain = sgqlc.types.Field(
        sgqlc.types.non_null(AllowedDomain),
        graphql_name="updateDomain",
        args=sgqlc.types.ArgDict(
            (
                (
                    "domain",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="domain",
                        default=None,
                    ),
                ),
                (
                    "default_group",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="defaultGroup",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_domain = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="removeDomain",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="input", default=None
                    ),
                ),
            )
        ),
    )
    create_saved_search = sgqlc.types.Field(
        sgqlc.types.non_null("SavedSearch"),
        graphql_name="createSavedSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
                (
                    "collection",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="collection",
                        default=None,
                    ),
                ),
                (
                    "search_string",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="searchString",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_saved_search = sgqlc.types.Field(
        sgqlc.types.non_null("SavedSearch"),
        graphql_name="deleteSavedSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_saved_search = sgqlc.types.Field(
        sgqlc.types.non_null("SavedSearch"),
        graphql_name="updateSavedSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
            )
        ),
    )
    share_saved_search = sgqlc.types.Field(
        sgqlc.types.non_null("SavedSearch"),
        graphql_name="shareSavedSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "user_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(GraphqlID),
                        graphql_name="userIds",
                        default=None,
                    ),
                ),
                (
                    "group_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(GraphqlID),
                        graphql_name="groupIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_commit_version_note = sgqlc.types.Field(
        sgqlc.types.non_null(Commit),
        graphql_name="updateCommitVersionNote",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID), graphql_name="id", default=None
                    ),
                ),
                (
                    "note",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="note", default=None
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_project = sgqlc.types.Field(
        sgqlc.types.non_null("Project"),
        graphql_name="createProject",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="name", default=None
                    ),
                ),
            )
        ),
    )
    update_project = sgqlc.types.Field(
        sgqlc.types.non_null("Project"),
        graphql_name="updateProject",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("name", sgqlc.types.Arg(String, graphql_name="name", default=None)),
                (
                    "user_id",
                    sgqlc.types.Arg(GraphqlID, graphql_name="userId", default=None),
                ),
                (
                    "description",
                    sgqlc.types.Arg(String, graphql_name="description", default=None),
                ),
            )
        ),
    )
    delete_project = sgqlc.types.Field(
        sgqlc.types.non_null("Project"),
        graphql_name="deleteProject",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    update_project_acl = sgqlc.types.Field(
        sgqlc.types.non_null("Project"),
        graphql_name="updateProjectAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_project_acl = sgqlc.types.Field(
        sgqlc.types.non_null("Project"),
        graphql_name="removeProjectAcl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AclInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    create_collection_sqarun = sgqlc.types.Field(
        sgqlc.types.non_null(CollectionSQARun),
        graphql_name="createCollectionSQARun",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionId",
                        default=None,
                    ),
                ),
                (
                    "email_notification",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Boolean),
                        graphql_name="emailNotification",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_collection_sqarun_status = sgqlc.types.Field(
        sgqlc.types.non_null(CollectionSQARun),
        graphql_name="updateCollectionSQARunStatus",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_sqa_run_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionSqaRunId",
                        default=None,
                    ),
                ),
                (
                    "status",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CollectionSQARunStatus),
                        graphql_name="status",
                        default=None,
                    ),
                ),
                (
                    "status_message",
                    sgqlc.types.Arg(String, graphql_name="statusMessage", default=None),
                ),
                (
                    "error_message",
                    sgqlc.types.Arg(String, graphql_name="errorMessage", default=None),
                ),
            )
        ),
    )
    complete_sqarun_success = sgqlc.types.Field(
        sgqlc.types.non_null(CollectionSQARun),
        graphql_name="completeSQARunSuccess",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_sqa_run_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionSqaRunId",
                        default=None,
                    ),
                ),
                (
                    "status_message",
                    sgqlc.types.Arg(String, graphql_name="statusMessage", default=None),
                ),
            )
        ),
    )
    complete_sqarun_fail = sgqlc.types.Field(
        sgqlc.types.non_null(CollectionSQARun),
        graphql_name="completeSQARunFail",
        args=sgqlc.types.ArgDict(
            (
                (
                    "collection_sqa_run_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="collectionSqaRunId",
                        default=None,
                    ),
                ),
                (
                    "status_message",
                    sgqlc.types.Arg(String, graphql_name="statusMessage", default=None),
                ),
                (
                    "error_message",
                    sgqlc.types.Arg(String, graphql_name="errorMessage", default=None),
                ),
            )
        ),
    )


class NTKConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("config_display_name", "config_data")
    config_display_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="configDisplayName"
    )
    config_data = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="configData"
    )


class ObjectDetectDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "classifier_name", "date")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    classifier_name = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="classifierName"
    )
    date = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="date")


class PaginatedFrames(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("frames", "count")
    frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Frame)), graphql_name="frames"
    )
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class Parent(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("name", "id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")


class Point(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("x", "y")
    x = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="x")
    y = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="y")


class Project(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "name",
        "acl",
        "user_id",
        "user_id_name",
        "created_by",
        "created_by_name",
        "created_at",
        "modified_at",
        "video_count",
        "recursive_video_count",
        "dataset_count",
        "recursive_dataset_count",
        "image_count",
        "recursive_image_count",
        "child_count",
        "recursive_child_count",
        "default_classifier",
        "path",
        "file_locker_files",
        "cover_image_url",
        "description",
        "word_cloud_url",
        "readme",
        "is_favorite",
        "favorite_count",
        "root_collection",
        "is_removed",
        "has_write_access",
        "has_admin_access",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    user_id_name = sgqlc.types.Field(String, graphql_name="userIdName")
    created_by = sgqlc.types.Field(String, graphql_name="createdBy")
    created_by_name = sgqlc.types.Field(String, graphql_name="createdByName")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Float, graphql_name="modifiedAt")
    video_count = sgqlc.types.Field(Int, graphql_name="videoCount")
    recursive_video_count = sgqlc.types.Field(Int, graphql_name="recursiveVideoCount")
    dataset_count = sgqlc.types.Field(Int, graphql_name="datasetCount")
    recursive_dataset_count = sgqlc.types.Field(
        Int, graphql_name="recursiveDatasetCount"
    )
    image_count = sgqlc.types.Field(Int, graphql_name="imageCount")
    recursive_image_count = sgqlc.types.Field(Int, graphql_name="recursiveImageCount")
    child_count = sgqlc.types.Field(Int, graphql_name="childCount")
    recursive_child_count = sgqlc.types.Field(Int, graphql_name="recursiveChildCount")
    default_classifier = sgqlc.types.Field(Classifier, graphql_name="defaultClassifier")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of("file"), graphql_name="fileLockerFiles"
    )
    cover_image_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="coverImageUrl"
    )
    description = sgqlc.types.Field(String, graphql_name="description")
    word_cloud_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="wordCloudUrl"
    )
    readme = sgqlc.types.Field(String, graphql_name="readme")
    is_favorite = sgqlc.types.Field(Boolean, graphql_name="isFavorite")
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    root_collection = sgqlc.types.Field(
        sgqlc.types.non_null(Collection), graphql_name="rootCollection"
    )
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")
    has_write_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasWriteAccess"
    )
    has_admin_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasAdminAccess"
    )


class Query(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "annotations_by_video_id",
        "annotations_by_frame_id",
        "collections",
        "collections_query_count",
        "collections_by_video_id",
        "collections_by_dataset_id",
        "collection",
        "get_first_nvideos",
        "get_first_nimages",
        "get_first_ndatasets",
        "get_collection_video_count",
        "get_collection_image_count",
        "get_collection_dataset_count",
        "collection_by_path",
        "dataset",
        "multi_datasets",
        "datasets",
        "datasets_query_count",
        "labelbox_frontends",
        "frames_exist_in_dataset",
        "get_dataset_jsonl",
        "get_dataset_videos_jsonl",
        "get_dataset_frames_jsonl",
        "dataset_frame",
        "dataset_frames",
        "dataset_frames_by_ids",
        "first_dataset_frame_id",
        "dataset_frames_only",
        "dataset_frames_with_context",
        "dataset_frame_count",
        "dataset_frames_query_count",
        "dataset_videos",
        "dataset_video_stats",
        "dataset_frames_exist_in_dataset",
        "datasheet_job_by_id",
        "datasheet_jobs_by_dataset_id",
        "datasheet_jobs_by_commit_id",
        "frames",
        "frame",
        "frame_with_search",
        "frames_by_ids",
        "frame_search",
        "get_frame_id_by_offset",
        "frame_count",
        "check_frames_by_md5",
        "group",
        "groups",
        "label_set",
        "label_sets",
        "label",
        "labels",
        "location",
        "settings",
        "queue_statistics",
        "validation_schema",
        "tags",
        "user",
        "user_by_email",
        "users",
        "favorites",
        "favorite",
        "favorite_videos",
        "favorite_frames",
        "favorite_datasets",
        "favorite_dataset_frames",
        "favorite_projects",
        "favorite_images",
        "favorite_folders",
        "video",
        "videos",
        "videos_query_count",
        "videos_by_ids",
        "videos_by_state",
        "domains",
        "domain_by_domain",
        "saved_searches",
        "saved_searches_by_user_id",
        "classifiers",
        "commit_history_by_id",
        "conservator_stats",
        "all_stats",
        "last_nstats",
        "git_diff_by_commit_id",
        "git_commit",
        "git_tree",
        "image",
        "images",
        "images_query_count",
        "images_by_ids",
        "projects",
        "projects_query_count",
        "project",
        "ntk_configs",
        "assets_by_md5s",
        "does_md5_exist",
    )
    annotations_by_video_id = sgqlc.types.Field(
        sgqlc.types.list_of(Annotation),
        graphql_name="annotationsByVideoId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    annotations_by_frame_id = sgqlc.types.Field(
        sgqlc.types.list_of(Annotation),
        graphql_name="annotationsByFrameId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    collections = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(Collection)),
        graphql_name="collections",
        args=sgqlc.types.ArgDict(
            (
                (
                    "parent_id",
                    sgqlc.types.Arg(GraphqlID, graphql_name="parentId", default=None),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    collections_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="collectionsQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "parent_id",
                    sgqlc.types.Arg(GraphqlID, graphql_name="parentId", default=None),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    collections_by_video_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Collection))),
        graphql_name="collectionsByVideoId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    collections_by_dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Collection))),
        graphql_name="collectionsByDatasetId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    collection = sgqlc.types.Field(
        Collection,
        graphql_name="collection",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    get_first_nvideos = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="getFirstNVideos",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("n", sgqlc.types.Arg(Int, graphql_name="n", default=None)),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    get_first_nimages = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="getFirstNImages",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("n", sgqlc.types.Arg(Int, graphql_name="n", default=None)),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    get_first_ndatasets = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Dataset)),
        graphql_name="getFirstNDatasets",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("n", sgqlc.types.Arg(Int, graphql_name="n", default=None)),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    get_collection_video_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="getCollectionVideoCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    get_collection_image_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="getCollectionImageCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    get_collection_dataset_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="getCollectionDatasetCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    collection_by_path = sgqlc.types.Field(
        Collection,
        graphql_name="collectionByPath",
        args=sgqlc.types.ArgDict(
            (
                (
                    "path",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="path", default=None
                    ),
                ),
            )
        ),
    )
    dataset = sgqlc.types.Field(
        Dataset,
        graphql_name="dataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    multi_datasets = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Dataset)),
        graphql_name="multiDatasets",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))
                        ),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    datasets = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(Dataset)),
        graphql_name="datasets",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
            )
        ),
    )
    datasets_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="datasetsQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
            )
        ),
    )
    labelbox_frontends = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("labelboxFrontend")),
        graphql_name="labelboxFrontends",
    )
    frames_exist_in_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="framesExistInDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "current_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="currentDatasetId",
                        default=None,
                    ),
                ),
                (
                    "selected_video_frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))
                        ),
                        graphql_name="selectedVideoFrameIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_dataset_jsonl = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="getDatasetJsonl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_dataset_videos_jsonl = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="getDatasetVideosJsonl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_dataset_frames_jsonl = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="getDatasetFramesJsonl",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    dataset_frame = sgqlc.types.Field(
        DatasetFrame,
        graphql_name="datasetFrame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("sort", sgqlc.types.Arg(String, graphql_name="sort", default=None)),
            )
        ),
    )
    dataset_frames = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrames),
        graphql_name="datasetFrames",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "page",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="page", default=None
                    ),
                ),
                (
                    "limit",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="limit", default=None
                    ),
                ),
                ("sort", sgqlc.types.Arg(String, graphql_name="sort", default=None)),
            )
        ),
    )
    dataset_frames_by_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="datasetFramesByIds",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    first_dataset_frame_id = sgqlc.types.Field(
        GraphqlID,
        graphql_name="firstDatasetFrameId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "page",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="page", default=None
                    ),
                ),
                (
                    "limit",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="limit", default=None
                    ),
                ),
                ("sort", sgqlc.types.Arg(String, graphql_name="sort", default=None)),
            )
        ),
    )
    dataset_frames_only = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrames),
        graphql_name="datasetFramesOnly",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "page",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="page", default=None
                    ),
                ),
                (
                    "limit",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="limit", default=None
                    ),
                ),
            )
        ),
    )
    dataset_frames_with_context = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="datasetFramesWithContext",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "index",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="index", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "context",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="context", default=None
                    ),
                ),
                ("sort", sgqlc.types.Arg(String, graphql_name="sort", default=None)),
            )
        ),
    )
    dataset_frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetFrameCount),
        graphql_name="datasetFrameCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    dataset_frames_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="datasetFramesQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    dataset_videos = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(DatasetVideo)),
        graphql_name="datasetVideos",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    dataset_video_stats = sgqlc.types.Field(
        sgqlc.types.non_null(DatasetVideoStatsResult),
        graphql_name="datasetVideoStats",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                (
                    "filename",
                    sgqlc.types.Arg(String, graphql_name="filename", default=None),
                ),
            )
        ),
    )
    dataset_frames_exist_in_dataset = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="datasetFramesExistInDataset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "source_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="sourceDatasetId",
                        default=None,
                    ),
                ),
                (
                    "target_dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="targetDatasetId",
                        default=None,
                    ),
                ),
                (
                    "selected_dataset_frame_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(GraphqlID),
                        graphql_name="selectedDatasetFrameIds",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    datasheet_job_by_id = sgqlc.types.Field(
        DatasheetJob,
        graphql_name="datasheetJobById",
        args=sgqlc.types.ArgDict(
            (
                (
                    "datasheet_job_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasheetJobId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    datasheet_jobs_by_dataset_id = sgqlc.types.Field(
        sgqlc.types.list_of(DatasheetJob),
        graphql_name="datasheetJobsByDatasetId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    datasheet_jobs_by_commit_id = sgqlc.types.Field(
        sgqlc.types.list_of(DatasheetJob),
        graphql_name="datasheetJobsByCommitId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "commit_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID), graphql_name="commitId", default=None
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    frames = sgqlc.types.Field(
        Frames,
        graphql_name="frames",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter",
                    sgqlc.types.Arg(FrameFilter, graphql_name="filter", default=None),
                ),
                (
                    "cursor",
                    sgqlc.types.Arg(String, graphql_name="cursor", default=None),
                ),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    frame = sgqlc.types.Field(
        Frame,
        graphql_name="frame",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FrameFilter),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
            )
        ),
    )
    frame_with_search = sgqlc.types.Field(
        Frame,
        graphql_name="frameWithSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "frame_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="frameId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    frames_by_ids = sgqlc.types.Field(
        sgqlc.types.list_of(Frame),
        graphql_name="framesByIds",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))
                        ),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    frame_search = sgqlc.types.Field(
        sgqlc.types.non_null(PaginatedFrames),
        graphql_name="frameSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "start_index",
                    sgqlc.types.Arg(Int, graphql_name="startIndex", default=None),
                ),
                (
                    "page",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="page", default=None
                    ),
                ),
                (
                    "limit",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="limit", default=None
                    ),
                ),
            )
        ),
    )
    get_frame_id_by_offset = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID),
        graphql_name="getFrameIdByOffset",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FrameIdByOffsetInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="frameCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "video_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="videoId",
                        default=None,
                    ),
                ),
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
            )
        ),
    )
    check_frames_by_md5 = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Md5Result))),
        graphql_name="checkFramesByMd5",
        args=sgqlc.types.ArgDict(
            (
                (
                    "md5s",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(String))
                        ),
                        graphql_name="md5s",
                        default=None,
                    ),
                ),
            )
        ),
    )
    group = sgqlc.types.Field(
        Group,
        graphql_name="group",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    groups = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Group))),
        graphql_name="groups",
    )
    label_set = sgqlc.types.Field(
        sgqlc.types.non_null(LabelSet),
        graphql_name="labelSet",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    label_sets = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(LabelSet)), graphql_name="labelSets"
    )
    label = sgqlc.types.Field(
        sgqlc.types.non_null(Label),
        graphql_name="label",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    labels = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Label)), graphql_name="labels"
    )
    location = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="location",
    )
    settings = sgqlc.types.Field(
        sgqlc.types.non_null("Settings"), graphql_name="settings"
    )
    queue_statistics = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("QueueDetails")),
        graphql_name="queueStatistics",
    )
    validation_schema = sgqlc.types.Field(String, graphql_name="validationSchema")
    tags = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase))
        ),
        graphql_name="tags",
    )
    user = sgqlc.types.Field("User", graphql_name="user")
    user_by_email = sgqlc.types.Field(
        "User",
        graphql_name="userByEmail",
        args=sgqlc.types.ArgDict(
            (
                (
                    "email",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String), graphql_name="email", default=None
                    ),
                ),
                (
                    "include_deleted",
                    sgqlc.types.Arg(
                        Boolean, graphql_name="includeDeleted", default=None
                    ),
                ),
            )
        ),
    )
    users = sgqlc.types.Field(sgqlc.types.list_of("User"), graphql_name="users")
    favorites = sgqlc.types.Field(
        sgqlc.types.list_of(Favorite), graphql_name="favorites"
    )
    favorite = sgqlc.types.Field(
        Favorite,
        graphql_name="favorite",
        args=sgqlc.types.ArgDict(
            (
                (
                    "favorite_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="favoriteId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    favorite_videos = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="favoriteVideos",
    )
    favorite_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Frame)), graphql_name="favoriteFrames"
    )
    favorite_datasets = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Dataset)),
        graphql_name="favoriteDatasets",
    )
    favorite_dataset_frames = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(DatasetFrame)),
        graphql_name="favoriteDatasetFrames",
    )
    favorite_projects = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Collection)),
        graphql_name="favoriteProjects",
    )
    favorite_images = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Image)), graphql_name="favoriteImages"
    )
    favorite_folders = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Collection)),
        graphql_name="favoriteFolders",
    )
    video = sgqlc.types.Field(
        "Video",
        graphql_name="video",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("src", sgqlc.types.Arg(String, graphql_name="src", default=None)),
            )
        ),
    )
    videos = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Video"))),
        graphql_name="videos",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
            )
        ),
    )
    videos_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="videosQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
            )
        ),
    )
    videos_by_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="videosByIds",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))
                        ),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    videos_by_state = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Video")),
        graphql_name="videosByState",
        args=sgqlc.types.ArgDict(
            (
                (
                    "state",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(VideoState),
                        graphql_name="state",
                        default=None,
                    ),
                ),
            )
        ),
    )
    domains = sgqlc.types.Field(
        sgqlc.types.non_null(Domains),
        graphql_name="domains",
        args=sgqlc.types.ArgDict(
            (
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    domain_by_domain = sgqlc.types.Field(
        AllowedDomain,
        graphql_name="domainByDomain",
        args=sgqlc.types.ArgDict(
            (
                (
                    "domain",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="domain",
                        default=None,
                    ),
                ),
            )
        ),
    )
    saved_searches = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("SavedSearch")),
        graphql_name="savedSearches",
    )
    saved_searches_by_user_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("SavedSearch")),
        graphql_name="savedSearchesByUserId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "user_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="userId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    classifiers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Classifier)),
        graphql_name="classifiers",
        args=sgqlc.types.ArgDict(
            (
                (
                    "object_detect_classifiers_only",
                    sgqlc.types.Arg(
                        Boolean,
                        graphql_name="objectDetectClassifiersOnly",
                        default=None,
                    ),
                ),
            )
        ),
    )
    commit_history_by_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Commit))),
        graphql_name="commitHistoryById",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    conservator_stats = sgqlc.types.Field(
        ConservatorStats,
        graphql_name="conservatorStats",
        args=sgqlc.types.ArgDict(
            (("id", sgqlc.types.Arg(ID, graphql_name="id", default=None)),)
        ),
    )
    all_stats = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(ConservatorStats)),
        graphql_name="allStats",
    )
    last_nstats = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(ConservatorStats)),
        graphql_name="lastNStats",
        args=sgqlc.types.ArgDict(
            (
                (
                    "number",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Int), graphql_name="number", default=None
                    ),
                ),
            )
        ),
    )
    git_diff_by_commit_id = sgqlc.types.Field(
        sgqlc.types.list_of(GitDiff),
        graphql_name="gitDiffByCommitId",
        args=sgqlc.types.ArgDict(
            (
                (
                    "commit_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID), graphql_name="commitId", default=None
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    git_commit = sgqlc.types.Field(
        GitCommit,
        graphql_name="gitCommit",
        args=sgqlc.types.ArgDict(
            (
                (
                    "commit_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="commitId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    git_tree = sgqlc.types.Field(
        GitTree,
        graphql_name="gitTree",
        args=sgqlc.types.ArgDict(
            (
                (
                    "tree_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(String),
                        graphql_name="treeId",
                        default=None,
                    ),
                ),
                (
                    "dataset_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID),
                        graphql_name="datasetId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    image = sgqlc.types.Field(
        Image,
        graphql_name="image",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
                ("src", sgqlc.types.Arg(String, graphql_name="src", default=None)),
            )
        ),
    )
    images = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Image))),
        graphql_name="images",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
            )
        ),
    )
    images_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="imagesQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.list_of(FilterItemInput),
                        graphql_name="filter",
                        default=None,
                    ),
                ),
                (
                    "collection_id",
                    sgqlc.types.Arg(
                        GraphqlID, graphql_name="collectionId", default=None
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
            )
        ),
    )
    images_by_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Image)),
        graphql_name="imagesByIds",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(GraphqlID))
                        ),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    projects = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Project)),
        graphql_name="projects",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    projects_query_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int),
        graphql_name="projectsQueryCount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "search_text",
                    sgqlc.types.Arg(String, graphql_name="searchText", default=None),
                ),
                ("page", sgqlc.types.Arg(Int, graphql_name="page", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=None)),
            )
        ),
    )
    project = sgqlc.types.Field(
        sgqlc.types.non_null(Project),
        graphql_name="project",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GraphqlID), graphql_name="id", default=None
                    ),
                ),
            )
        ),
    )
    ntk_configs = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(NTKConfig)), graphql_name="ntkConfigs"
    )
    assets_by_md5s = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Md5Asset)),
        graphql_name="assetsByMd5s",
        args=sgqlc.types.ArgDict(
            (
                (
                    "md5s",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(
                            sgqlc.types.list_of(sgqlc.types.non_null(Md5String))
                        ),
                        graphql_name="md5s",
                        default=None,
                    ),
                ),
            )
        ),
    )
    does_md5_exist = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean),
        graphql_name="doesMd5Exist",
        args=sgqlc.types.ArgDict(
            (
                (
                    "md5",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Md5String),
                        graphql_name="md5",
                        default=None,
                    ),
                ),
            )
        ),
    )


class QueueDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "name",
        "ready_message_count",
        "un_acked_message_count",
        "total_message_count",
        "consumers",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    ready_message_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="readyMessageCount"
    )
    un_acked_message_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="unAckedMessageCount"
    )
    total_message_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="totalMessageCount"
    )
    consumers = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="consumers")


class Repository(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "user_id", "dataset_id", "master", "repo_state")
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="userId")
    dataset_id = sgqlc.types.Field(
        sgqlc.types.non_null(GraphqlID), graphql_name="datasetId"
    )
    master = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="master")
    repo_state = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="repoState"
    )


class SavedSearch(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "user_id",
        "name",
        "acl",
        "search_string",
        "collection",
        "modified_at",
        "created_at",
        "user",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="userId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    search_string = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="searchString"
    )
    collection = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="collection"
    )
    modified_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="modifiedAt"
    )
    created_at = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="createdAt"
    )
    user = sgqlc.types.Field(sgqlc.types.non_null("User"), graphql_name="user")


class Segment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "start_frame_index", "end_frame_index")
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    start_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="startFrameIndex"
    )
    end_frame_index = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="endFrameIndex"
    )


class Settings(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "commit",
        "jira_collector_url",
        "max_login_attempts",
        "demo_mode",
        "top_banner",
        "labelbox_enabled",
        "sqa_enabled",
        "object_detect_enabled",
        "conservator_insights_docs_url",
    )
    commit = sgqlc.types.Field(String, graphql_name="commit")
    jira_collector_url = sgqlc.types.Field(String, graphql_name="jiraCollectorUrl")
    max_login_attempts = sgqlc.types.Field(Int, graphql_name="maxLoginAttempts")
    demo_mode = sgqlc.types.Field(Boolean, graphql_name="demoMode")
    top_banner = sgqlc.types.Field(String, graphql_name="topBanner")
    labelbox_enabled = sgqlc.types.Field(Boolean, graphql_name="labelboxEnabled")
    sqa_enabled = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="sqaEnabled"
    )
    object_detect_enabled = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="objectDetectEnabled"
    )
    conservator_insights_docs_url = sgqlc.types.Field(
        String, graphql_name="conservatorInsightsDocsUrl"
    )


class SignedUrl(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("signed_url", "url")
    signed_url = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="signedUrl"
    )
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")


class Source(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("type", "meta")
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="type")
    meta = sgqlc.types.Field(sgqlc.types.non_null(AnnotationMeta), graphql_name="meta")


class User(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "email",
        "name",
        "role",
        "is_white_listed",
        "api_key",
        "groups",
        "is_local",
        "is_removed",
        "has_lambda",
        "labelbox_api_key",
        "sign_in_lock_until",
        "sign_in_is_locked",
        "last_successful_sign_in",
        "organization",
        "notes",
        "user_data_stats",
        "user_data_stats_running",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    email = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="email")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="role")
    is_white_listed = sgqlc.types.Field(Boolean, graphql_name="isWhiteListed")
    api_key = sgqlc.types.Field(String, graphql_name="apiKey")
    groups = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(Group)), graphql_name="groups"
    )
    is_local = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isLocal")
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")
    has_lambda = sgqlc.types.Field(Boolean, graphql_name="hasLambda")
    labelbox_api_key = sgqlc.types.Field(String, graphql_name="labelboxApiKey")
    sign_in_lock_until = sgqlc.types.Field(Date, graphql_name="signInLockUntil")
    sign_in_is_locked = sgqlc.types.Field(Boolean, graphql_name="signInIsLocked")
    last_successful_sign_in = sgqlc.types.Field(
        Date, graphql_name="lastSuccessfulSignIn"
    )
    organization = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="organization"
    )
    notes = sgqlc.types.Field(String, graphql_name="notes")
    user_data_stats = sgqlc.types.Field("UserDataStats", graphql_name="userDataStats")
    user_data_stats_running = sgqlc.types.Field(
        Boolean, graphql_name="userDataStatsRunning"
    )


class UserDataStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "video_count",
        "frame_count",
        "video_raw_size",
        "frame_raw_size",
        "video_preview_size",
        "frame_preview_size",
        "last_updated_at",
    )
    video_count = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="videoCount"
    )
    frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="frameCount"
    )
    video_raw_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="videoRawSize"
    )
    frame_raw_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="frameRawSize"
    )
    video_preview_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="videoPreviewSize"
    )
    frame_preview_size = sgqlc.types.Field(
        sgqlc.types.non_null(Float), graphql_name="framePreviewSize"
    )
    last_updated_at = sgqlc.types.Field(
        sgqlc.types.non_null(Date), graphql_name="lastUpdatedAt"
    )


class Video(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "id",
        "filename",
        "url",
        "thumbnail_url",
        "preview_video_url",
        "md5",
        "preview_md5",
        "preview_file_size",
        "cover_image_url",
        "state",
        "object_detect_state",
        "object_detect_error",
        "metadata",
        "created_at",
        "modified_at",
        "user_id",
        "user_id_name",
        "user_id_email",
        "uploaded_by",
        "uploaded_by_name",
        "uploaded_by_email",
        "frames",
        "frames_count",
        "frame_count",
        "annotations_count",
        "human_annotations_count",
        "name",
        "description",
        "location",
        "width",
        "height",
        "tags",
        "filmed_at",
        "raw_exif",
        "frame_rate",
        "duration",
        "file_locker_files",
        "annotation_import_state",
        "annotation_import_state_modified_at",
        "highest_target_id",
        "custom_metadata",
        "collections",
        "segments",
        "datasets",
        "acl",
        "shared_with",
        "file_size",
        "object_detect_batches_total",
        "object_detect_batches_done",
        "spectrum",
        "asset_type",
        "is_favorite",
        "favorite_count",
        "object_detect_details",
        "is_removed",
        "prediction_label_data",
        "annotation_label_data",
        "process_video_error_message",
        "annotation_import_error_message",
        "readme",
        "inherited_acl",
        "annotated_frames",
        "un_annotated_frames",
        "empty_frames",
        "key_frames",
        "owner",
        "qa_change_requested_frames",
        "qa_approved_frames",
        "has_write_access",
        "has_admin_access",
        "qa_pending_frames",
        "flagged_frames",
        "labelbox_dataset_id",
        "labelbox_project_id",
        "labelbox_import_state",
        "labelbox_export_state",
        "labelbox_export_error",
        "labelbox_remove_state",
        "labelbox_update_state",
        "full_res_mp4_url",
        "full_res_mp4_status",
        "preview_generation_status",
        "processed_with_agc",
        "attached_label_set_ids",
        "attached_label_sets",
        "recalculate_stats_state",
        "allow_annotations_outside_frame",
        "allow_duplicate_target_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="id")
    filename = sgqlc.types.Field(String, graphql_name="filename")
    url = sgqlc.types.Field(String, graphql_name="url")
    thumbnail_url = sgqlc.types.Field(String, graphql_name="thumbnailUrl")
    preview_video_url = sgqlc.types.Field(String, graphql_name="previewVideoUrl")
    md5 = sgqlc.types.Field(String, graphql_name="md5")
    preview_md5 = sgqlc.types.Field(String, graphql_name="previewMd5")
    preview_file_size = sgqlc.types.Field(Float, graphql_name="previewFileSize")
    cover_image_url = sgqlc.types.Field(String, graphql_name="coverImageUrl")
    state = sgqlc.types.Field(VideoState, graphql_name="state")
    object_detect_state = sgqlc.types.Field(String, graphql_name="objectDetectState")
    object_detect_error = sgqlc.types.Field(String, graphql_name="objectDetectError")
    metadata = sgqlc.types.Field(String, graphql_name="metadata")
    created_at = sgqlc.types.Field(Float, graphql_name="createdAt")
    modified_at = sgqlc.types.Field(Float, graphql_name="modifiedAt")
    user_id = sgqlc.types.Field(GraphqlID, graphql_name="userId")
    user_id_name = sgqlc.types.Field(String, graphql_name="userIdName")
    user_id_email = sgqlc.types.Field(String, graphql_name="userIdEmail")
    uploaded_by = sgqlc.types.Field(String, graphql_name="uploadedBy")
    uploaded_by_name = sgqlc.types.Field(String, graphql_name="uploadedByName")
    uploaded_by_email = sgqlc.types.Field(String, graphql_name="uploadedByEmail")
    frames = sgqlc.types.Field(
        sgqlc.types.list_of(Frame),
        graphql_name="frames",
        args=sgqlc.types.ArgDict(
            (
                ("id", sgqlc.types.Arg(GraphqlID, graphql_name="id", default=None)),
                (
                    "frame_index",
                    sgqlc.types.Arg(Int, graphql_name="frameIndex", default=None),
                ),
                (
                    "start_frame_index",
                    sgqlc.types.Arg(Int, graphql_name="startFrameIndex", default=None),
                ),
            )
        ),
    )
    frames_count = sgqlc.types.Field(Int, graphql_name="framesCount")
    frame_count = sgqlc.types.Field(Int, graphql_name="frameCount")
    annotations_count = sgqlc.types.Field(Int, graphql_name="annotationsCount")
    human_annotations_count = sgqlc.types.Field(
        Int, graphql_name="humanAnnotationsCount"
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    location = sgqlc.types.Field(String, graphql_name="location")
    width = sgqlc.types.Field(Int, graphql_name="width")
    height = sgqlc.types.Field(Int, graphql_name="height")
    tags = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(StringLowerCase)), graphql_name="tags"
    )
    filmed_at = sgqlc.types.Field(Date, graphql_name="filmedAt")
    raw_exif = sgqlc.types.Field(String, graphql_name="rawExif")
    frame_rate = sgqlc.types.Field(Float, graphql_name="frameRate")
    duration = sgqlc.types.Field(String, graphql_name="duration")
    file_locker_files = sgqlc.types.Field(
        sgqlc.types.list_of("file"), graphql_name="fileLockerFiles"
    )
    annotation_import_state = sgqlc.types.Field(
        AnnotationImportState, graphql_name="annotationImportState"
    )
    annotation_import_state_modified_at = sgqlc.types.Field(
        Date, graphql_name="annotationImportStateModifiedAt"
    )
    highest_target_id = sgqlc.types.Field(Int, graphql_name="highestTargetId")
    custom_metadata = sgqlc.types.Field(String, graphql_name="customMetadata")
    collections = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(GraphqlID)), graphql_name="collections"
    )
    segments = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Segment)), graphql_name="segments"
    )
    datasets = sgqlc.types.Field(sgqlc.types.list_of(Dataset), graphql_name="datasets")
    acl = sgqlc.types.Field(Acl, graphql_name="acl")
    shared_with = sgqlc.types.Field(AclPermissionLevels, graphql_name="sharedWith")
    file_size = sgqlc.types.Field(Float, graphql_name="fileSize")
    object_detect_batches_total = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesTotal"
    )
    object_detect_batches_done = sgqlc.types.Field(
        Int, graphql_name="objectDetectBatchesDone"
    )
    spectrum = sgqlc.types.Field(String, graphql_name="spectrum")
    asset_type = sgqlc.types.Field(String, graphql_name="assetType")
    is_favorite = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isFavorite"
    )
    favorite_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="favoriteCount"
    )
    object_detect_details = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(ObjectDetectDetails)),
        graphql_name="objectDetectDetails",
    )
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")
    prediction_label_data = sgqlc.types.Field(
        sgqlc.types.list_of("labelCount"), graphql_name="predictionLabelData"
    )
    annotation_label_data = sgqlc.types.Field(
        sgqlc.types.list_of("labelCount"), graphql_name="annotationLabelData"
    )
    process_video_error_message = sgqlc.types.Field(
        String, graphql_name="processVideoErrorMessage"
    )
    annotation_import_error_message = sgqlc.types.Field(
        String, graphql_name="annotationImportErrorMessage"
    )
    readme = sgqlc.types.Field(String, graphql_name="readme")
    inherited_acl = sgqlc.types.Field(Acl, graphql_name="inheritedAcl")
    annotated_frames = sgqlc.types.Field(Int, graphql_name="annotatedFrames")
    un_annotated_frames = sgqlc.types.Field(Int, graphql_name="unAnnotatedFrames")
    empty_frames = sgqlc.types.Field(Int, graphql_name="emptyFrames")
    key_frames = sgqlc.types.Field(Int, graphql_name="keyFrames")
    owner = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="owner")
    qa_change_requested_frames = sgqlc.types.Field(
        Int, graphql_name="qaChangeRequestedFrames"
    )
    qa_approved_frames = sgqlc.types.Field(Int, graphql_name="qaApprovedFrames")
    has_write_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasWriteAccess"
    )
    has_admin_access = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="hasAdminAccess"
    )
    qa_pending_frames = sgqlc.types.Field(Int, graphql_name="qaPendingFrames")
    flagged_frames = sgqlc.types.Field(Int, graphql_name="flaggedFrames")
    labelbox_dataset_id = sgqlc.types.Field(String, graphql_name="labelboxDatasetId")
    labelbox_project_id = sgqlc.types.Field(String, graphql_name="labelboxProjectId")
    labelbox_import_state = sgqlc.types.Field(
        String, graphql_name="labelboxImportState"
    )
    labelbox_export_state = sgqlc.types.Field(
        String, graphql_name="labelboxExportState"
    )
    labelbox_export_error = sgqlc.types.Field(
        String, graphql_name="labelboxExportError"
    )
    labelbox_remove_state = sgqlc.types.Field(
        String, graphql_name="labelboxRemoveState"
    )
    labelbox_update_state = sgqlc.types.Field(
        String, graphql_name="labelboxUpdateState"
    )
    full_res_mp4_url = sgqlc.types.Field(String, graphql_name="fullResMp4Url")
    full_res_mp4_status = sgqlc.types.Field(String, graphql_name="fullResMp4Status")
    preview_generation_status = sgqlc.types.Field(
        String, graphql_name="previewGenerationStatus"
    )
    processed_with_agc = sgqlc.types.Field(String, graphql_name="processedWithAGC")
    attached_label_set_ids = sgqlc.types.Field(
        sgqlc.types.list_of(GraphqlID), graphql_name="attachedLabelSetIds"
    )
    attached_label_sets = sgqlc.types.Field(
        sgqlc.types.list_of(LabelSet), graphql_name="attachedLabelSets"
    )
    recalculate_stats_state = sgqlc.types.Field(
        String, graphql_name="recalculateStatsState"
    )
    allow_annotations_outside_frame = sgqlc.types.Field(
        Boolean, graphql_name="allowAnnotationsOutsideFrame"
    )
    allow_duplicate_target_id = sgqlc.types.Field(
        Boolean, graphql_name="allowDuplicateTargetId"
    )


class VideoStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("_id", "filename", "frame_count", "asset_type", "is_removed")
    _id = sgqlc.types.Field(sgqlc.types.non_null(GraphqlID), graphql_name="_id")
    filename = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="filename")
    frame_count = sgqlc.types.Field(
        sgqlc.types.non_null(Int), graphql_name="frameCount"
    )
    asset_type = sgqlc.types.Field(
        sgqlc.types.non_null(String), graphql_name="assetType"
    )
    is_removed = sgqlc.types.Field(Boolean, graphql_name="isRemoved")


class file(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("url", "name", "view_url")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    view_url = sgqlc.types.Field(String, graphql_name="viewUrl")


class labelCount(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("label", "count")
    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="label")
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class labelboxFrontend(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("id", "name", "is_default")
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_default = sgqlc.types.Field(Boolean, graphql_name="isDefault")


########################################################################
# Unions
########################################################################

########################################################################
# Schema Entry Points
########################################################################
schema.query_type = Query
schema.mutation_type = Mutation
schema.subscription_type = None
