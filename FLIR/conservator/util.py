import hashlib
import multiprocessing
import os
import logging
import requests
import tqdm


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
        s += o.__class__.__name__
        for field in o.underlying_type.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace("\n", "\n    ")

    elif hasattr(o, "__field_names__"):
        s += o.__class__.__name__
        for field in o.__field_names__:
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


class FileDownloadException(Exception):
    pass


def download_file(path, name, url, remote_md5, silent=False, no_meter=False):
    path = os.path.abspath(path)
    file_path = os.path.join(path, name)
    os.makedirs(path, exist_ok=True)

    if remote_md5 and os.path.exists(file_path):
        logger.debug(f"Comparing {name} to {url}")
        local_md5 = md5sum_file(file_path)
        if local_md5 == remote_md5:
            logger.info(f"Skip {name} (already downloaded)")
            return True

    logger.debug(f"Downloading {name} from {url}")
    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        if not silent:
            raise FileDownloadException(url)
        else:
            logger.debug(f"Skipped silent FileDownloadException for url: {url}")
            return False
    size = int(r.headers.get("content-length", 0))
    size_mb = int(size / 1024 / 1024)
    progress = tqdm.tqdm(total=size, disable=no_meter)
    progress.set_description(f"Downloading {name} ({size_mb:.2f} MB)")
    chunk_size = 1024 * 1024
    with open(file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            progress.update(len(chunk))
            fd.write(chunk)
    progress.close()
    return True


def download_files(files, process_count=None, no_meter=False):
    # files = (path, name, url, remote_md5)
    # where remote_md5 is empty string if unknown
    pool = multiprocessing.Pool(process_count)  # defaults to CPU count
    args = [(*file, True, no_meter) for i, file in enumerate(files)]
    results = pool.starmap(download_file, args)
    return results


def upload_file(path, url):
    path = os.path.abspath(path)
    logger.info(f"Uploading '{path}'")
    with open(path, "rb") as f:
        response = requests.put(url, f)
    assert response.ok
    logger.info(f"Completed upload of '{path}'")
    return response


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
