import functools
import os
import shlex

import click
import readline

from typing import Optional

from FLIR.conservator.cli.managers import fields_request
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.wrappers import Collection, Video, Image
from FLIR.conservator.wrappers.collection import InvalidRemotePathException

pwd = "/"
ctx = None
conservator: Optional[Conservator] = None
current_collection: Optional[Collection] = None
root_collections: [Collection] = None


def complete(value, state):
    args = shlex.split(value)
    if len(args) > 1:
        to_complete = args[-1]
    else:
        to_complete = ""
    paths = get_child_paths()
    filtered = list(filter(lambda name: name.startswith(to_complete), paths))
    if state <= len(filtered):
        v = filtered[state].replace(" ", "\\ ")
        return f"{args[0]} {v}"


readline.set_completer_delims("")
readline.set_completer(complete)
readline.parse_and_bind("tab: complete")


def print_status(message):
    end = "\033[" + str(len(message)) + "D"
    click.secho(message + end, fg="yellow", nl=False)


def clear_status():
    click.echo("\033[0K", nl=False)


def get_root_collections():
    global root_collections
    if root_collections is None:
        click.secho("Loading root collections...", fg="yellow")
        projects = conservator.projects.all().including_fields("root_collection.name")
        root_collections = [project.root_collection for project in projects]
    return root_collections


def get_child_collections():
    if pwd == "/":
        return get_root_collections()

    if current_collection is None:
        return []

    return current_collection.children


def get_videos():
    if not hasattr(current_collection, "videos"):
        print_status("Loading videos...")
        vid_q = current_collection.get_videos(fields="name")
        current_collection.videos = list(vid_q)
        clear_status()
    return current_collection.videos


def get_images():
    if not hasattr(current_collection, "images"):
        print_status("Loading images...")
        img_q = current_collection.get_images(fields="name")
        current_collection.images = list(img_q)
        clear_status()
    return current_collection.images


def get_child_media():
    if current_collection is None:
        return []
    return get_videos() + get_images()


def get_child_paths():
    collection_paths = [collection.name + "/" for collection in get_child_collections()]
    media_paths = [media.name for media in get_child_media()]
    return collection_paths + media_paths


def get_from_path(path):
    if path == ".":
        return current_collection
    for collection in get_child_collections():
        if path == collection.name or path == collection.name + "/":
            return collection
    for media in get_child_media():
        if path == media.name:
            return media
    return None


def requires_valid_collection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_collection is None:
            click.secho("Not in a valid Collection", fg="red")
            return
        func(*args, **kwargs)

    return wrapper


@click.group("$", add_help_option=False)
def shell():
    pass


@shell.command("help", help="Print this message")
def _help():
    click.echo(shell.get_help(ctx))


@shell.command("pwd", help="Print the working directory")
def _pwd():
    click.echo(pwd)


@shell.command(help="Switch working directory")
@click.argument("path", nargs=-1)
def cd(path):
    path = " ".join(path)
    global pwd, current_collection
    new_path = os.path.abspath(os.path.join(pwd, path))
    new_path = new_path.replace("//", "/")
    if new_path == "/":
        pwd = "/"
        current_collection = None
        return

    fields = FieldsRequest()
    fields.include_field("path", "id", "children.name", "children.path")
    try:
        collection = conservator.collections.from_remote_path(new_path, fields=fields)
    except InvalidRemotePathException:
        click.secho(f"Invalid path '{new_path}'", fg="red")
        return
    pwd = collection.path
    current_collection = collection


@shell.command("fields", help="Get fields of the current collection")
@requires_valid_collection
@fields_request
def _fields(fields):
    current_collection.populate(fields=fields)
    click.echo(current_collection)


@shell.command("details", help="Get details on a file or collection")
@click.argument("filename", default=".")
def details(filename):
    item = get_from_path(filename)
    if item is None:
        click.secho(f"Couldn't find '{filename}' in current collection", fg="red")
        return
    detail_fields = FieldsRequest()
    if isinstance(item, Collection):
        detail_fields.include_field(
            "name",
            "path",
            "owner",
            "created_by_name",
            "recursive_video_count",
            "recursive_dataset_count",
            "recursive_image_count",
            "recursive_child_count",
            "description",
        )
        item.populate(detail_fields)
        click.echo(f"Name: {item.name}")
        click.echo(f"Collection ID: {item.id}")
        click.echo(f"Path: {item.path}")
        click.echo(f"Owner: {item.owner}")
        click.echo(f"Creator: {item.created_by_name}")
        click.echo(f"Total Videos: {item.recursive_video_count}")
        click.echo(f"Total Images: {item.recursive_image_count}")
        click.echo(f"Total Datasets: {item.recursive_dataset_count}")
        click.echo(f"Total Child Collections: {item.recursive_child_count}")
        click.echo(f"Description: {item.description}")
    elif isinstance(item, Video) or isinstance(item, Image):
        detail_fields.include_field(
            "name",
            "owner",
            "uploaded_by_name",
            "file_size",
            "location",
            "tags",
            "spectrum",
            "description",
        )
        item.populate(detail_fields)
        click.echo(f"Name: {item.name}")
        click.echo(f"{item.__class__.__name__} ID: {item.id}")
        click.echo(f"Owner: {item.owner}")
        click.echo(f"Uploader: {item.uploaded_by_name}")
        click.echo(f"File Size: {item.file_size / 1024 / 1024:.2f} MB")
        click.echo(f"Location: {item.location}")
        click.echo(f"Tags: {item.tags}")
        click.echo(f"Spectrum: {item.spectrum}")
        click.echo(f"Description: {item.description}")
    else:
        click.echo("Unknown type")


@shell.command(help="List collections, videos, images, and file locker files")
def ls():
    click.secho(".", fg="blue")

    if pwd != "/":
        click.secho("..", fg="blue")

    for child in get_child_collections():
        click.secho(child.name + "/", fg="blue")

    if current_collection is None:
        return

    for video in get_videos():
        click.secho(video.name, fg="green")

    for image in get_images():
        click.secho(image.name, fg="bright_green")

    file_fields = FieldsRequest()
    file_fields.include_field("file_locker_files.name")
    current_collection.populate(file_fields)
    for file in current_collection.file_locker_files:
        click.secho(file.name, fg="yellow")


@shell.command("files", help="List file locker files")
@click.option(
    "-u", "--url", is_flag=True, help="If specified, also print a download URL"
)
@requires_valid_collection
def _files(url):
    fields = FieldsRequest()
    fields.include_field("file_locker_files.name")
    if url:
        fields.include_field("file_locker_files.url")
    current_collection.populate(fields)

    if len(current_collection.file_locker_files) == 0:
        click.secho("Collection has no files", fg="red")
        return

    for file in current_collection.file_locker_files:
        line = file.name
        if url:
            line += f" {file.url}"
        click.echo(line)


@shell.command("collections", help="List child collections")
def _collections():
    if pwd == "/":
        click.secho("In root directory, listing all projects...", fg="yellow")
        for project in conservator.projects.all().including_fields("name"):
            click.echo(project.name + "/")
        return

    if current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return

    if len(current_collection.children) == 0:
        click.secho("Collection has no child collections", fg="red")
        return

    for child in current_collection.children:
        click.echo(child.name + "/")


@shell.command("videos", help="List videos")
@click.option("-s", "--size", is_flag=True, help="Print file size")
@requires_valid_collection
def _videos(size):
    video_fields = FieldsRequest()
    video_fields.include_field("name")
    if size:
        video_fields.include_field("file_size")
    for video in current_collection.get_videos(video_fields):
        line = video.name
        if size:
            mb = int(video.file_size // 1024 // 1024)
            line += f"\t({mb} mb)"
        click.echo(line)


@shell.command("images", help="List images")
@requires_valid_collection
def _images():
    for image in get_images():
        click.echo(image.name)


@shell.command("open", help="Open in browser")
def _open():
    if pwd == "/":
        url = conservator.get_url()
    else:
        url = conservator.get_collection_url(current_collection)
    click.secho(f"Opening {url}...", fg="yellow")
    click.launch(url)


@shell.command(help="List child collection paths recursively")
def tree():
    collections = []
    if pwd == "/":
        for project in conservator.projects.all().including_fields(
            "root_collection.path"
        ):
            collections.append(project.root_collection)
    elif current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return
    else:
        collections.append(current_collection)

    child_paths = FieldsRequest()
    child_paths.include_field("children.path", "children.id")
    while len(collections) > 0:
        collection = collections.pop()
        click.echo(collection.path)
        collection.populate(child_paths)
        collections.extend(collection.children)


@shell.command(help="Upload a local file to the current collection")
@click.argument("localpath", default=".")
@click.argument("type", default="video")
@click.option(
    "-r",
    "--remote-name",
    help="If specified, the name of the remote file. Defaults to the local file name",
)
@requires_valid_collection
def upload(local_path, type, remote_name):
    if type == "video":
        conservator.videos.upload(
            local_path, collection=current_collection, remote_name=remote_name
        )


@shell.command(help="Download the current collection")
@click.argument("localpath", default=".")
@click.option("-d", "--datasets", is_flag=True, help="Pull datasets")
@click.option(
    "-v", "--video-metadata", is_flag=True, help="Include image and video metadata"
)
@click.option("-f", "--associated-files", is_flag=True, help="Include associated files")
@click.option("-m", "--media", is_flag=True, help="Include media (videos and images)")
@click.option(
    "-r", "--recursive", is_flag=True, help="Include child collections recursively"
)
@requires_valid_collection
def download(localpath, datasets, video_metadata, associated_files, media, recursive):
    current_collection.download(
        localpath, datasets, video_metadata, associated_files, media, recursive
    )


def run_shell_command(command):
    args = shlex.split(command)
    if len(args) == 0:
        return
    try:
        global ctx
        ctx = shell.make_context("$", args)
        shell.invoke(ctx)
    except click.exceptions.Exit:
        pass
    except KeyboardInterrupt:
        click.secho("Interrupted", fg="red")
    except Exception as e:
        click.secho("Unexpected Exception: " + str(e), fg="red")


@click.command(help="An interactive shell for exploring conservator")
def interactive():
    global conservator
    ctx_obj = click.get_current_context().obj
    conservator = Conservator.create(ctx_obj["config_name"])

    click.secho(
        """This is an interactive conservator "shell" that simulates the directory\n"""
        """structure of Conservator's collections. Type "help" to see available commands.""",
        fg="cyan",
    )

    domain = conservator.get_domain()

    click.secho(f"Loading identity from {domain}...", fg="yellow")
    username = conservator.get_user().name
    get_root_collections()

    while True:
        user = click.style(f"{username}@{domain}:", fg="magenta", bold=True)
        path = click.style(f"{pwd}", fg="blue", bold=True)
        end = click.unstyle("$ ")
        command = input(user + path + end)
        run_shell_command(command)


if __name__ == "__main__":
    interactive()
