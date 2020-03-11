#!/usr/bin/env python3
import click
import json
import os
import subprocess
import shutil

from FLIR.conservator_cli.lib import conservator_api as fca

def clone_dataset(user_email, id, name, parent_folder_path, conservator_token):
    save = os.getcwd()
    os.chdir(parent_folder_path)
    if os.path.exists(name):
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

def download_video_metadata(collection_id, parent_folder_path, conservator_token):
    videos = fca.get_videos_from_collection(collection_id, conservator_token)
    video_names = []
    for video in videos:
        metadata = fca.get_video_metadata(video["id"], conservator_token)["metadata"]
        obj = json.loads(metadata)
        obj["videos"][0]["name"] = video["name"]
        filename = ".".join(video["name"].split(".")[:-1] + ["json"])
        video_names.append(filename)
        with open(os.path.join(parent_folder_path, filename), "w") as file:
            json.dump(obj, file, indent=4, separators=(',', ': '))
    return video_names

def download_collection_recursive(user_email, collection_id, parent_folder_path, conservator_token, include_datasets, include_images,
                               include_video_metadata, include_associated_files, overwrite, tab_number=0):
    data = fca.get_collection_by_id(collection_id, conservator_token)
    collection_path=os.path.join(parent_folder_path, data["name"])
    print("\t"*tab_number + "Entering: {}".format(collection_path))
    os.makedirs(collection_path, exist_ok=True)

    child_names = []
    if include_video_metadata:
        child_names += download_video_metadata(data["id"], collection_path, conservator_token)

    datasets = fca.get_datasets_from_collection(data["id"], conservator_token)
    child_names += [dataset["name"] for dataset in datasets]
    if include_datasets:
        for dataset in datasets:
            print("\t"*tab_number + "Cloning: {}".format(dataset["name"]))
            clone_dataset(user_email.replace("@", "%40"), dataset["id"], dataset["name"],
                          collection_path, conservator_token)

    for id in data["childIds"]:
        child_name = download_collection_recursive(user_email, id, collection_path, conservator_token,
                                   include_datasets, include_images, include_video_metadata, include_associated_files, overwrite, tab_number+1)
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
            fca.download_file(os.path.join(collection_path, file["name"]), file["url"], conservator_token, tab_number=tab_number+1)
    print("\t"*tab_number + "Exiting: {}".format(collection_path))
    return data["name"]

@click.command()
@click.argument('collection_path')
@click.option('-u', '--email', prompt="Conservator Email", help="The email of the conservator account to use for auth")
@click.option('-t', '--conservator_token', prompt="Conservator Token", help="Conservator API Token")
@click.option('-d', '--include_datasets', help="download datasets", is_flag=True)
@click.option('-i', '--include_images', help="download images", is_flag=True)
@click.option('-m', '--include_video_metadata', help="download video metadata", is_flag=True)
@click.option('-a', '--include_associated_files', help="download associated files", is_flag=True)
@click.option('-o', '--overwrite', help="remove local files not present in conservator", is_flag=True)
def download_collection_main(collection_path, email, conservator_token, include_datasets, include_images, include_video_metadata,
                          include_associated_files, overwrite):
    data = fca.get_collection_by_path(collection_path, conservator_token)
    if not data:
        print("Collection {} not found!".format(collection_path))
        exit()
    download_collection_recursive(email, data["id"], "", conservator_token, include_datasets, include_images,
                               include_video_metadata, include_associated_files, overwrite)

if __name__ == "__main__":
    download_collection_main()
