from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.paginated_query import PaginatedQuery
from FLIR.conservator.generated.schema import Query, DatasetFrame

conservator = Conservator.default()
fields = FieldsRequest()
fields.include_field("dataset_frames.frame_id")
fields.include_field("dataset_frames.width")
fields.include_field("dataset_frames.height")
query_results = PaginatedQuery(
    conservator,
    query=Query.dataset_frames_only,
    unpack_field="dataset_frames",
    fields=fields,
    id="RkAXSN4ychHgiNkMk",
)

for frame in query_results:
    print(frame)
