from FLIR.conservator.connection import ConservatorConnection
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.generated.schema import Query, Project
from sgqlc.operation import Operation


def test_add_fields_simple():
    op = Operation(Query)
    q = op.project
    q(id="123")
    fields = FieldsRequest()
    fields.include_field("name")
    fields.add_fields_to_request(q)
    assert 'project(id: "123")' in str(op)
    assert 'name' in str(op)
    assert 'repository' not in str(op)


def test_add_fields_simple_exclude():
    op = Operation(Query)
    q = op.project
    q(id="123")
    fields = FieldsRequest()
    fields.exclude_field("file_locker_files", "root_collection")
    fields.add_fields_to_request(q)
    assert 'project(id: "123")' in str(op)
    assert 'fileLockerFiles' not in str(op)
    assert 'rootCollection' not in str(op)
    assert 'createdBy' in str(op)


def test_should_include_path():
    a = FieldsRequest()
    a.include_field("repository", "id")
    assert a.should_include_path("repository")
    assert a.should_include_path("repository.master")
    assert a.should_include_path("id")
    assert not a.should_include_path("name")

    b = FieldsRequest()
    b.include_field("repository", "id")
    b.exclude_field("repository.master")
    assert b.should_include_path("repository")
    assert not b.should_include_path("repository.master")
    assert b.should_include_path("id")
    assert not b.should_include_path("name")

    c = FieldsRequest()
    c.include_field("name")
    c.exclude_field("name")
    assert not b.should_include_path("name")
