import multiprocessing
import os

import requests
import tqdm


def to_clean_string(o, first=True):
    s = ''
    if isinstance(o, dict):
        s += "{"
        for key, value in o.items():
            s += f"\n{key}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')
        s += "\n}"
    elif hasattr(o.__class__, 'underlying_type'):
        for field in o.underlying_type.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')

    elif hasattr(o, '__field_names__'):
        for field in o.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')
    elif isinstance(o, list) or isinstance(o, tuple):
        s += "["
        for v in o:
            s += f"\n{to_clean_string(v, False)}"
        s = s.replace('\n', '\n    ')
        s += "\n]"
    else:
        s += f"{o}"
        s = s.replace('\n', '\n    ')

    if first and s.startswith('\n'):
        s = s[1:]

    return s


class FileDownloadException(Exception):
    pass


def download_file(path, name, url, silent=True):
    path = os.path.abspath(path)
    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        if not silent:
            raise FileDownloadException(url)
        else:
            return False
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
    return True


def download_files(files, process_count=None):
    # files = (path, name, url)
    pool = multiprocessing.Pool(process_count)  # defaults to CPU count
    results = pool.starmap(download_file, files)
    return results
