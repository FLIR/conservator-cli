from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest

conservator = Conservator.default()
fields = FieldsRequest()
fields.include_field("dataset_frames.frame_id")
fields.include_field("dataset_frames.width")
fields.include_field("dataset_frames.height")
fields.include_field("dataset_frames.annotations.bounding_box")
fields.include_field("dataset_frames.annotations.labels")

dataset = conservator.datasets.from_id("RkAXSN4ychHgiNkMk")

for frame in dataset.get_frames(fields=fields):
    print(frame)
