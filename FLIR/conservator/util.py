import hashlib
import logging
import semver
import requests

from itertools import zip_longest
from FLIR.conservator.version import version as cli_ver

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


def get_conservator_cli_version():
    # Get latest version from PyPi programatically
    # See https://stackoverflow.com/a/62571316
    response = requests.get("https://pypi.org/pypi/conservator-cli/json")
    return response.json()["info"]["version"]


def compare_conservator_cli_version():
    current_version = semver.VersionInfo.parse(cli_ver)
    latest_version = semver.VersionInfo.parse(get_conservator_cli_version())

    if latest_version == current_version:
        return True
    if latest_version < current_version:
        logger.warning("You are using Conservator-cli version %s", current_version)
        logger.warning("Please upgrade to the latest version %s", latest_version)
        return False
    if latest_version > current_version:
        logger.warning(
            "You are using an unreleased version of Conservator-cli (%s)",
            current_version,
        )
        logger.warning(
            "Please be aware that this version may not be supported in the future"
        )
        logger.warning(
            "For reference, the current supported version of Conservator-cli is %s",
            latest_version,
        )
        return False
