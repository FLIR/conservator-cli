import hashlib
import logging

from itertools import zip_longest

logger = logging.getLogger(__name__)


def to_clean_string(o, first=True):
    s = ""
    if isinstance(o, dict):
        s += "{"
        for key, value in o.items():
            s += f"\n{key}: {to_clean_string(value, False)}"
        s = s.replace("\n", "\n    ")
        s += "\n}"
    elif hasattr(o.__class__, "underlying_type"):
        s += o._instance.__class__.__name__
        for field in o.underlying_type.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace("\n", "\n    ")
    elif isinstance(o, list) or isinstance(o, tuple):
        s += "["
        for v in o:
            s += f"\n{to_clean_string(v, False)}"
        s = s.replace("\n", "\n    ")
        s += "\n]"
    else:
        s += f"{o}"
        s = s.replace("\n", "\n    ")

    if first and s.startswith("\n"):
        s = s[1:]

    return s


def md5sum_file(path, block_size=1024 * 1024):
    hasher = hashlib.md5()
    with open(path, "rb") as fp:
        block = fp.read(block_size)
        while block:
            hasher.update(block)
            block = fp.read(block_size)
    return hasher.hexdigest()


def base_convert(b, n):
    output = []
    while n:
        r = int(n % b)
        output.append(r)
        n = int(n / b)
    return output


def chunks(list, size):
    """
    Simple one-line function to divide a list of items into chunks
    of a specified size.

    Once the input list is exhausted, the last list in the output
    iterator will be padded by None's to make up the size difference.

    :param list: list to be split into smaller "chunk" lists
    :param size: the desired size of the chunk lists
    :return: an iterator of these chunks.

    :Example:

    chunks(['a', 'b', 'c'], 2) will return an iterator containing
    ['a', 'b'] and ['c', None]

    .. note:: Adapted from  https://stackoverflow.com/a/312644
    """
    return zip_longest(*[iter(list)] * size, fillvalue=None)
