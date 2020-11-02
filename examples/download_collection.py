from conservator import Conservator

conservator = Conservator.default()

sqa = conservator.collections.search("SQA").with_fields("name").first()
print("Found SQA Collection:", sqa.name)

path = "."
sqa.download_assets(path, include_associated_files=True, recursive=True, include_datasets=True, include_metadata=True, pull=False)


