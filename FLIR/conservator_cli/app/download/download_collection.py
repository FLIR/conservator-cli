#!/usr/bin/env python3
import click
import json
import os
import subprocess
import shutil

from FLIR.conservator_cli.lib import conservator_api as fca

def clone_dataset(user_email, conservator_token, id, name, path):
    save = os.getcwd()
    os.chdir(path)
    if os.path.exists(name):
        print("Path exists")
        os.chdir(name)
        subp = subprocess.call(["git", "pull"])
        subp = subprocess.call(["./cvc.py", "pull"])
        subp = subprocess.call(["./cvc.py", "pull"])
    else:
        subp = subprocess.call(["git", "clone", "https://{}@flirconservator.com/git/dataset_{}".format(user_email, id), "{}".format(name)])
        os.chdir(name)
        subp = subprocess.call(["./cvc.py", "remote", "add", "https://{}:{}@flirconservator.com/dvc".format(user_email, conservator_token)])
        subp = subprocess.call(["./cvc.py", "pull"])
        subp = subprocess.call(["./cvc.py", "pull"])
    os.chdir(save)

def download_videos(collection_id, path, conservator_token):
    videos = fca.get_videos_from_collection(collection_id, conservator_token)
    for video in videos:
        metadata = fca.get_video_metadata(video["id"], conservator_token)["metadata"]
        obj = json.loads(metadata)
        print(obj.keys())
        obj["videos"][0]["name"] = video["name"]
        filename = ".".join(video["name"].split(".")[:-1] + ["json"])
        with open(os.path.join(path, filename), "w") as file:
            json.dump(obj, file, indent=4, separators=(',', ': '))

def download_collection_recursive(user_email, collection_id, path, conservator_token, include_datasets, include_images,
                               include_videos, include_associated_files, overwrite):
    data = fca.get_collection_by_id(collection_id, conservator_token)
    collection_path=os.path.join(path, data["name"])
    os.makedirs(collection_path, exist_ok=True)

    if include_videos:
        download_videos(data["id"], collection_path, conservator_token)

    child_names = []
    datasets = fca.get_datasets_from_collection(data["id"], conservator_token)
    child_names += [dataset["name"] for dataset in datasets]
    if include_datasets:
        for dataset in datasets:
            clone_dataset(user_email.replace("@", "%40"), conservator_token, dataset["id"], dataset["name"],
                          collection_path)
            print(dataset)

    for id in data["childIds"]:
        child_name = download_collection_recursive(user_email, id, collection_path, conservator_token,
                                   include_datasets, include_images, include_videos, include_associated_files, overwrite)
        child_names.append(child_name)

    if(overwrite):
        list_dir = os.listdir(collection_path)
        dataset_names = [dataset["name"] for dataset in datasets]
        for node in list_dir:
            if node in dataset_names or node in child_names :
                continue
            try:
                shutil.rmtree(os.path.join(collection_path, node))
            except:
                os.remove(os.path.join(collection_path, node))

    if include_associated_files:
        for file in data["fileLockerFiles"]:
            fca.download_file(os.path.join(path, data["name"], file["name"]), file["url"], conservator_token)

    return data["name"]

@click.command()
@click.argument('collection_path')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-d', '--include_datasets', help="download datasets", is_flag=True)
@click.option('-i', '--include_images', help="download images", is_flag=True)
@click.option('-v', '--include_videos', help="download videos", is_flag=True)
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
@click.option('-o', '--overwrite', help="remove local files not present in conservator", is_flag=True)
def download_collection_main(collection_path, email, conservator_token, include_datasets, include_images, include_videos,
                          include_associated_files, overwrite):
    data = fca.get_collection_by_path(collection_path, conservator_token)
    if not data:
        print("Collection {} not found!".format(collection_path))
        exit()
    download_collection_recursive(email, data["id"], "", conservator_token, include_datasets, include_images,
                               include_videos, include_associated_files, overwrite)

if __name__ == "__main__":
    download_collection_main()
