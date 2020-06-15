import itertools
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def flatten(list2d):
    return list(itertools.chain(*list2d))


def read_json_file(path):
    with open(path, 'r') as file:
        content = json.load(file)
    return content

def save_to_json_file(content, path):
    with open(path, 'w') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)


def get_lines_from_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        lines = map(str.strip, lines)
        lines = map(lambda x: '_'.join(x.split()), lines)
        lines = map(str.lower, lines)
        lines = list(set(lines))
    return lines
