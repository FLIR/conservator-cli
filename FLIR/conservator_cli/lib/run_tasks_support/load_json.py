import json
import os

""" Utility function for load JSON file, with
support for { "$ref": "$ENVIRON/xyz.json" } fields. """

def flatten_refs(obj):
    """ Flattens { "$ref": "filename.json" } fields """

    flat = obj
    if isinstance(obj, dict):
        if "$ref" in obj.keys() and isinstance(obj["$ref"], str):
            filename = obj["$ref"]
            flat = load_json(filename)

        for k, v in obj.items():
            if k != "$ref":
                flat[k] = flatten_refs(obj[k])

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = flatten_refs(obj[i])

    return flat


def load_json(filename):
    """ Loads JSON and flattens refs """
    with open(os.path.expandvars(filename)) as fp:
        obj = json.load(fp)
        return flatten_refs(obj)


if __name__ == "__main__":
    import sys
    print("test: {}".format(sys.argv[1]))
    print(load_json(sys.argv[1]))

