# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import hashlib
import logging
import os
import platform
import sys

from pathlib import Path
from itertools import zip_longest

import semver
import requests

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


def chunks(list_to_chunk, chunk_size):
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
    return zip_longest(*[iter(list_to_chunk)] * chunk_size, fillvalue=None)


def get_conservator_cli_version():
    # Get latest version from PyPi programatically
    # See https://stackoverflow.com/a/62571316
    response = requests.get("https://pypi.org/pypi/conservator-cli/json", timeout=10)
    return response.json()["info"]["version"]


def compare_conservator_cli_version():
    installed_version = semver.VersionInfo.parse(cli_ver)
    released_version = semver.VersionInfo.parse(get_conservator_cli_version())

    installed_version_simple = semver.VersionInfo.parse(
        f"{installed_version.major}.{installed_version.minor}.{installed_version.patch}"
    )

    if released_version == installed_version:
        return True
    if released_version == installed_version_simple and installed_version.build:
        logger.warning(
            "You are using an unreleased version of Conservator-cli (%s)",
            installed_version,
        )
        logger.warning(
            "Please be aware that this version may not be supported in the future"
        )
        logger.warning(
            "For reference, the current supported version of Conservator-cli is %s",
            released_version,
        )
        return False
    if released_version < installed_version_simple:
        logger.warning(
            "You are using an unreleased version of Conservator-cli (%s)",
            installed_version,
        )
        logger.warning(
            "Please be aware that this version may not be supported in the future"
        )
        logger.warning(
            "For reference, the current supported version of Conservator-cli is %s",
            released_version,
        )
        return False
    if released_version > installed_version_simple:
        logger.warning(
            "You are using a deprecated version of Conservator-cli (%s)",
            installed_version,
        )
        logger.warning("Please upgrade to the latest version (%s)", released_version)
        return False


def check_platform():
    current_platform = platform.system()

    if current_platform.lower() == "windows":
        print("Conservator-CLI is currently only supported on Windows through WSL.")
        print(
            "Please see https://flir.github.io/conservator-cli/usage/installation.html#installation-on-windows for details"
        )
        sys.exit(1)


def check_dir_access(path_to_check):
    if os.path.exists(path_to_check):
        return os.access(path_to_check, os.W_OK)
    else:
        parent_path = Path(path_to_check).parent
        return os.access(parent_path, os.W_OK)
