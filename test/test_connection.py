from FLIR.conservator.connection import ConservatorConnection
from FLIR.conservator.generated.schema import Query, Project
from sgqlc.operation import Operation


def test_add_fields_simple():
    op = Operation(Query)
    q = op.project
    q(id="123")
    ConservatorConnection.recursive_add_fields(q, include_fields=("name",))
    assert 'project(id: "123")' in str(op)
    assert 'name' in str(op)
    assert 'repository' not in str(op)


def test_add_fields_simple_exclude():
    op = Operation(Query)
    q = op.project
    q(id="123")
    ConservatorConnection.recursive_add_fields(q, exclude_fields=("file_locker_files",))
    assert 'project(id: "123")' in str(op)
    assert 'fileLockerFiles' not in str(op)
    assert 'repository' in str(op)

