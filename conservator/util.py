import keyword
import os
import re

import requests
import tqdm
from sgqlc.types import BaseItem


def to_clean_string(o, first=True):
    s = ''
    if isinstance(o, dict):
        s += "{"
        for key, value in o.items():
            s += f"\n{key}: {to_clean_string(value, False)}"
        s += "\n}"
    elif hasattr(o.__class__, 'underlying_type'):
        for field in o.underlying_type.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"

    elif hasattr(o, '__field_names__'):
        for field in o.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
    elif isinstance(o, list) or isinstance(o, tuple):
        s += "["
        for v in o:
            s += f"\n{to_clean_string(v, False)}"
        s += "\n]"
    else:
        s += f"{o}"

    s = s.replace('\n', '\n    ')

    if first and s.startswith('\n'):
        s = s[1:]

    return s


re_camel_case_words = re.compile('([^A-Z]+|[A-Z]+[^A-Z]*)')


def graphql_to_python(name):
    """This code copied from SGQLC codegen"""
    s = []
    for w in re_camel_case_words.findall(name):
        s.append(w.lower())
    name = '_'.join(s)
    if keyword.iskeyword(name):
        return name + '_'
    return name


def download_file(path, name, url):
    r = requests.get(url, stream=True)
    size = int(r.headers["content-length"])
    size_mb = int(size / 1024 / 1024)
    progress = tqdm.tqdm(total=size)
    progress.set_description(f"Downloading {name} ({size_mb:.2f} MB)")
    chunk_size = 1024
    with open(os.path.join(path, name), 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            progress.update(len(chunk))
            fd.write(chunk)
    progress.close()
