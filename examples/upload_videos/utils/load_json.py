""" Utility function for load JSON file, with
support for { "$ref": "$ENVIRON/xyz.json" } fields.
Originally from: https://github.com/FLIR/task_runner/blob/main/FLIR/task_runner/lib/load_json.py
"""
import json
import os


def flatten_refs(obj):
    """Flattens { "$ref": "filename.json" } fields"""

    flat = obj
    if isinstance(obj, dict):
        if "$ref" in obj.keys():
            ref = obj["$ref"]
            if not isinstance(ref, str):
                raise Exception(f'Reference ($ref) is not a string: "{ref}"')
            flat = load_json(path=ref)

        for key in obj.keys():
            if key != "$ref":
                flat[key] = flatten_refs(obj[key])

    elif isinstance(obj, list):
        for counter, value in enumerate(obj):
            obj[counter] = flatten_refs(value)

    return flat


def load_json(path):
    """Loads JSON and flattens refs"""
    expanded_path = os.path.expandvars(path)
    if not os.path.exists(expanded_path):
        raise Exception(f'Path could not be found: "{path}" ({expanded_path})')

    if not os.path.isfile(expanded_path):
        raise Exception(f'Path is not a valid file: "{path}" ({expanded_path})')

    with open(expanded_path, encoding="UTF-8") as json_file:
        try:
            obj = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            raise Exception(f'Could not parse JSON file: "{path}" ({expanded_path})') from e
        return flatten_refs(obj)


if __name__ == "__main__":
    import sys

    print("test: {sys.argv[1]}")
    print(load_json(sys.argv[1]))
