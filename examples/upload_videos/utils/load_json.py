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

        for k, v in obj.items():
            if k != "$ref":
                flat[k] = flatten_refs(obj[k])

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = flatten_refs(obj[i])

    return flat


def load_json(path):
    """Loads JSON and flattens refs"""
    expanded_path = os.path.expandvars(path)
    if not os.path.exists(expanded_path):
        raise Exception(f'Path could not be found: "{path}" ({expanded_path})')

    if not os.path.isfile(expanded_path):
        raise Exception(f'Path is not a valid file: "{path}" ({expanded_path})')

    with open(expanded_path) as fp:
        obj = json.load(fp)
        return flatten_refs(obj)


if __name__ == "__main__":
    import sys

    print("test: {}".format(sys.argv[1]))
    print(load_json(sys.argv[1]))
