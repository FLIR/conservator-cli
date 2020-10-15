#!/usr/bin/env python
import sys
import os
import getopt
import json
import hashlib
import time
import random
import shutil
import argparse
try:
    from eventlet import patcher, GreenPool
    patcher.monkey_patch(all=True)
    import requests
    from PIL import Image
except ImportError:
    print("Missing requirements run 'pip install requests eventlet Pillow'")
    exit(1)
# Conservator Version Control


def log(str):
    print(str)


def get_config():

    config = json.load(open(os.path.join('.cvc', 'config.json')))

    return config


def load_staging():

    staging_file = os.path.join('.cvc', 'staging.json')

    if os.path.exists(staging_file):
        return json.load(open(staging_file))

    return {'files': {}}


def save_staging(data):

    staging_file = os.path.join('.cvc', 'staging.json')

    f = open(staging_file, 'w')
    json.dump(data, f, indent=4, sort_keys=True)

    f.close()


def save_index(data):

    staging_file = os.path.join('index.json')

    f = open(staging_file, 'w')
    json.dump(data, f, indent=4, sort_keys=True, separators=(',', ': '))

    f.close()


def update_config(data):

    # Cheeck if we have a config
    if os.path.exists(os.path.join('.cvc', 'config.json')):
        confData = get_config()

    else:
        # Check if we have a .cvc folder
        if not os.path.exists('.cvc'):
            log("Creating cvc folder")
            os.makedirs('.cvc')

        confData = {}

    confData.update(data)

    f = open(os.path.join('.cvc', 'config.json'), 'w')
    json.dump(data, f, indent=4, sort_keys=True)

    f.close()


def check_cache(key):
    filename = os.path.join(*['.cvc', 'cache', key[0], key[1]])

    if os.path.exists(filename):
        log("{} found in cache".format("".join(key)))
        return filename
    else:
        return False


def save_to_cache(key, content):
    filepath = os.path.join(*['.cvc', 'cache', key[0]])
    if not os.path.exists(filepath):
        log("Making Dir {}".format(filepath))
        os.makedirs(filepath)

    filename = os.path.join(filepath, key[1])
    open(filename, 'wb').write(content)
    log("Saved as {}".format(filename))
    return filename


def download_image(config, md5, videoId, datasetFrameId, frameIndex, ext, folder='data'):
    print("downloading {}".format(md5))
    key = [md5[:2], md5[2:]]
    filename = check_cache(key)
    if not filename:
        url = '/'.join([config['url']] + key)
        r = requests.get(url, allow_redirects=True)
        if r.status_code == 200:
            filename = save_to_cache(key, r.content)
        else:
            log("ERROR: Could not Download {} status: {}".format(url, r.status_code))
            return "ERROR"

    imageFilename = 'video-{}-frame-{:06d}-{}.{}'.format(
        videoId, frameIndex, datasetFrameId, ext)

    if os.path.exists(os.path.join(folder, imageFilename)):
        log("File {} exists".format(imageFilename))
        return filename

    # Hard link named image file
    os.link(filename, os.path.join(folder, imageFilename))
    return filename


def base_convert(b, n):
    output = []
    r = 0
    while n:
        r = int(n % b)
        output.append(r)
        n = int(n / b)
    return output


def generate_id():
    charset = '23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz'

    t = time.time()
    id = [charset[i] for i in base_convert(55, t)[::-1]]
    for i in range(17 - len(id)):
        id.append(random.choice(charset))
    return ''.join(id)


def get_file_info(filename):

    # Check if this is a file or directory
    if not os.path.exists(filename):
        log("filename '{}' does not exist".format(filename))
        return False
    if os.path.isdir(filename):
        log("omitting directory '{}'".format(filename))
        return False

    # Make sure file is a JPG
    try:
        img = Image.open(filename)
    except Exception:
        log("filename '{}' is not an image".format(filename))
        return False

    if img.format != 'JPEG':
        log("filename '{}' is not an JPEG".format(filename))
        return False

    image_data = {}
    size = img.size
    image_data['filename'] = filename
    image_data['height'] = size[0]
    image_data['width'] = size[1]
    image_data['fileSize'] = os.path.getsize(filename)
    image_data['md5'] = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    return image_data


def check_if_exists(config, url):
    # User http head to check if this md5 is already in conservator
    r = requests.head(url)

    if r.status_code == 302:
        return True

    return False


def upload(config, frameData):

    md5 = frameData['md5']
    key = [md5[:2], md5[2:]]
    url = '/'.join([config['url']] + key)

    # Check if this md5 is in conservator
    if check_if_exists(config, url):
        log("File Exists in conservator, skipping upload")
        return True

    # Split any path of the file
    filename = frameData['filename'].split('/')[-1]

    headers = {'Content-type': 'image/jpeg',
               'x-amz-meta-originalfilename': filename}
    log('Uploading file {}'.format(filename))
    f = open(frameData['filename'], 'rb')
    r = requests.put(url, allow_redirects=False, headers=headers, data=f)
    if r.status_code == 302:
        # For some reason the auto redirect dosen't work so we need to do this manual
        rurl = r.headers['location']
        # If we have a relative url append prefix
        if not rurl.startswith("http"):
            rurl = '/'.join(url.split('/')[:3]) + rurl
        f.seek(0)
        r = requests.put(rurl, allow_redirects=False, headers=headers, data=f)
    if r.status_code != 200:
        log('Error Uploading file {}'.format(frameData['filename']))
        log(r.text)
        return False
    if r.headers['ETag'] != '"{}"'.format(md5):
        log("ETag does not match md5 for file {}".format(
            frameData['filename']))
        return False
    return True


def get_max_frame_index(index):

    # Check only the 'loose' frames and return the max frameIndex
    frameIndex = 0

    for f in index.get('frames', []):
        if f['datasetFrameId'] == f['videoMetadata']['frameId']:
            if f['videoMetadata']['frameIndex'] > frameIndex:
                frameIndex = f['videoMetadata']['frameIndex']

    return frameIndex


def cvc_help(args, subparsers):
    msg = """ Conservator version control
CVC Commands:
    add         Add files to upload to Conservator
    pull        Pull in images. Downloads 8bit frames by default, use --all-frames to include 16-bit (raw) frames or --only-analytics to download only 16-bit frames. Use --pool-size <int> to change download streams. Default is 10
    push        Upload staged files to Conservator and modify index.json
    status      Display staged files
    help        Display this message
    remote      Add/Remove Remote
          """
    print(msg)


def cvc_pull(args, subparsers):
    log("cvc_pull")
    config = get_config()
    results = []
    # default do not download 16bit images
    downloadAnalytics = False
    # default download 8bit images
    download8Bit = True

    if args.all_frames:
        log("Including Analytics")
        downloadAnalytics = True

    if args.only_analytics:
        log("Downloading only analytics")
        downloadAnalytics = True
        download8Bit = False

    # Check that image data folders exist
    if not os.path.exists('data') and download8Bit == True:
        os.makedirs('data')

    # Check that analytics image data folders exist
    if not os.path.exists('analyticsData') and downloadAnalytics == True:
        os.makedirs('analyticsData')

    pool = GreenPool(size=10)
    if args.pool_size:
        pool = GreenPool(size=args.pool_size)

    with open('index.json') as indexFile:
        datasetData = json.load(indexFile)
        for frame in datasetData.get('frames', []):
            videoMetadata = frame.get('videoMetadata', {})
            if download8Bit:
                results.append(pool.spawn(download_image, config, frame['md5'],
                                          videoMetadata.get('videoId', ''),
                                          frame['datasetFrameId'],
                                          videoMetadata['frameIndex'], 'jpg'))
            if downloadAnalytics and ('analyticsMd5' in frame):
                results.append(pool.spawn(download_image, config, frame['analyticsMd5'],
                                          videoMetadata.get('videoId', ''),
                                          frame['datasetFrameId'],
                                          videoMetadata['frameIndex'], 'tiff', folder='analyticsData'))

    pool.waitall()
    # See if we have any errors
    downloadedFiles = [x.wait() for x in results]
    num_errors = downloadedFiles.count('ERROR')
    log("Number of Files: {}, Errors: {}".format(
        len(downloadedFiles)-num_errors, num_errors))


def cvc_remote(args, subparsers):

    url = args.url
    log("Adding URL {}".format(url))
    update_config({'url': url})


def cvc_add(args, subparsers):

    staging_data = load_staging()

    for i in sys.argv[2:]:
        file_data = get_file_info(i)
        if file_data:
            log("Adding {}".format(i))
            staging_data['files'][i] = file_data

    save_staging(staging_data)


def cvc_push(args, subparsers):

    config = get_config()
    staging_data = load_staging()

    index = json.load(open('index.json'))
    datasetId = index['datasetId']
    videoId = datasetId

    frameIndex = get_max_frame_index(index)
    log("Max frameIndex is {}".format(frameIndex))

    frameIndex += 1

    # Check that image data folders exist
    if not os.path.exists('data'):
        os.makedirs('data')

    if len(staging_data['files']) == 0:
        log("No files to push")
        return

    for f in staging_data['files']:

        frameData = staging_data['files'][f]
        origFilename = frameData['filename']

        # Upload to S3
        if not upload(config, frameData):
            continue

        # Copy to data folder with proper name
        datasetFrameId = generate_id()
        frameId = datasetFrameId

        imageFilename = 'video-{}-frame-{:06d}-{}.{}'.format(
            videoId, frameIndex, datasetFrameId, 'jpg')
        log(imageFilename)
        shutil.copyfile(origFilename, os.path.join('data', imageFilename))

        # Add frame to index

        newFrame = {"datasetFrameId": datasetFrameId,
                    "isEmpty": False,
                    "isFlagged": False,
                    "md5": frameData['md5'],
                    "width": frameData['width'],
                    "height": frameData['height'],
                    "fileSize": frameData['fileSize'],
                    "videoMetadata": {
                        "frameId": frameId,
                        "videoId": videoId,
                        "frameIndex": frameIndex
                    },
                    "annotations": []}

        index['frames'].append(newFrame)
        log("Added datasetFrameId {}".format(datasetFrameId))

        frameIndex += 1

    log("Writing new frames to index.json")
    save_index(index)
    # Clear staging
    save_staging({'files': {}})


def cvc_status(args, subparsers):

    staging_data = load_staging()

    log("Staged Files:")

    for f in staging_data['files']:
        log("    {}".format(staging_data['files'][f]['filename']))


def main():
    if len(sys.argv) < 2:
        cvc_help(False, False)
        sys.exit()

    parser = argparse.ArgumentParser(description='Conservator version control')

    subparsers = parser.add_subparsers()

    cvc_help_parser = subparsers.add_parser('help')
    cvc_help_parser.set_defaults(func=cvc_help)

    cvc_status_parser = subparsers.add_parser('status')
    cvc_status_parser.set_defaults(func=cvc_status)

    cvc_push_parser = subparsers.add_parser('push')
    cvc_push_parser.set_defaults(func=cvc_push)

    cvc_add_parser = subparsers.add_parser('add')
    cvc_add_parser.add_argument(
        "files", type=str, nargs='+', help="path to one or more files")
    cvc_add_parser.set_defaults(func=cvc_add)

    cvc_remote_parser = subparsers.add_parser('remote')
    cvc_remote_parser.add_argument("remote_command", type=str, choices=['add'])
    cvc_remote_parser.add_argument(
        "url", type=str, help="path to one or more files")
    cvc_remote_parser.set_defaults(func=cvc_remote)

    cvc_pull_parser = subparsers.add_parser('pull')
    cvc_pull_parser_group = cvc_pull_parser.add_mutually_exclusive_group()
    cvc_pull_parser.add_argument("--pool-size", type=int, help="default is 10")
    cvc_pull_parser_group.add_argument(
        "--all-frames", action="store_true", help="include analytics frames")
    cvc_pull_parser_group.add_argument(
        "--only-analytics", action="store_true", help="download only analytics frames")
    cvc_pull_parser.set_defaults(func=cvc_pull)

    args = parser.parse_args()

    args.func(args, subparsers)


if __name__ == '__main__':
    main()
