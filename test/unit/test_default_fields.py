"""
These tests are very simple. They ensure that the default fields
in FieldsManager are valid.
"""
from FLIR.conservator.fields_manager import FieldsManager

from FLIR.conservator.generated.schema import Query
from sgqlc.operation import Operation


def test_scalar():
    # collections_query_count returns an Int, which is a Scalar.
    op = Operation(Query)
    FieldsManager.select_default_fields(op.collections_query_count)


def test_enum():
    # AnnotationImportState is an Enum.
    op = Operation(Query)
    FieldsManager.select_default_fields(op.image.annotation_import_state)


def test_acl():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.image.acl)


def test_collection():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.collection)


def test_dataset():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.dataset)


def test_dataset_frame():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.dataset_frame)


def test_dataset_frames():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.dataset_frames)


def test_frame():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.frame)


def test_frames():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.frames)


def test_group():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.group)


def test_image():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.image)


def test_label_set():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.label_set)


def test_paginated_frames():
    # frame_search returns PaginatedFrames
    op = Operation(Query)
    FieldsManager.select_default_fields(op.frame_search)


def test_project():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.project)


def test_user():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.user)


def test_repository():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.dataset.repository)


def test_video():
    op = Operation(Query)
    FieldsManager.select_default_fields(op.video)
