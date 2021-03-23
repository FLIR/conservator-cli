from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import Query
from sgqlc.operation import Operation


def test_prepare_query_simple():
    op = Operation(Query)
    q = op.project
    q(id="123")
    fields = FieldsRequest()
    fields.include_field("name")
    fields.prepare_query(q)
    assert 'project(id: "123")' in str(op)
    assert "name" in str(op)
    assert "repository" not in str(op)


def test_prepare_query_simple_exclude():
    op = Operation(Query)
    q = op.project
    q(id="123")
    fields = FieldsRequest()
    fields.include_field("file_locker_files", "acl")
    fields.exclude_field("file_locker_files")
    fields.prepare_query(q)
    assert 'project(id: "123")' in str(op)
    assert "fileLockerFiles" not in str(op)
    assert "acl" in str(op)
