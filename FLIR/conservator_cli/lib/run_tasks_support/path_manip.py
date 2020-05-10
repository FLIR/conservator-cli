import os
import re

import shutil


def expand_path(path):
    """
    Gets the absolute path of the parameter passed in replacing path variables.
    This includes home directory if included, which python does not recognize by default
    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.normpath(path))))


def expandvars(path):
    """
    Removes commented arguments from the path and expands path variables
    """
    return re.sub(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*', '', os.path.expandvars(path))


def base_filename(path):
    """
    Returns the filename of path without leading directories or file extension
    e.g.

    base_filename('/tmp/ke.log') = 'ke'
    """
    return os.path.splitext(os.path.basename(expand_path(path)))[0]


def move(orig, dest):
    """
    Moves the original file to destintaion using shutil instead of os.path
    "Safe move"
    """
    shutil.move(expand_path(orig), expand_path(dest))


def json_expandvars(o):
    """
    Expands environment variables in json-decoded object values
    """
    if isinstance(o, dict):
        return {json_expandvars(k): json_expandvars(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [json_expandvars(v) for v in o]
    elif isinstance(o, type("")):
        return os.path.expandvars(o)
    else:
        return o

