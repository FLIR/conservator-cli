import os
import shlex

import click
import readline

from typing import Optional

from FLIR.conservator.cli.managers import fields_request
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.types import Collection

pwd = "/"
ctx = None
conservator: Optional[Conservator] = None
current_collection: Optional[Collection] = None
root_collections: [Collection] = None


def complete(value, state):
    args = shlex.split(value)
    to_complete = args[-1]
    names = [child.name + "/" for child in get_child_collections()]
    filtered = list(filter(lambda name: name.startswith(to_complete), names))
    if state <= len(filtered):
        v = filtered[state].replace(" ", "\\ ")
        return f"{args[0]} {v}"


readline.set_completer_delims("")
readline.set_completer(complete)
readline.parse_and_bind("tab: complete")


def get_root_collections():
    global root_collections
    if root_collections is None:
        click.secho("Loading root collections...", fg='yellow')
        projects = conservator.projects.all().including_fields("root_collection.name")
        root_collections = [project.root_collection for project in projects]
    return root_collections


def get_child_collections():
    if pwd == "/":
        return get_root_collections()

    if current_collection is None:
        return []

    return current_collection.children


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
    collection = conservator.collections.from_remote_path(new_path, fields)
    if collection is None:
        click.secho(f"Invalid path '{new_path}'", fg="red")
        return
    pwd = collection.path
    current_collection = collection


@shell.command(help="Get information on the current collection")
@fields_request
def info(fields):
    collection = conservator.collections.from_remote_path(pwd, fields)
    if collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return
    click.echo(collection)


@shell.command(help="List collections, videos, images, and file locker files")
def ls():
    click.secho(".", fg='blue')

    if pwd != "/":
        click.secho("..", fg='blue')

    for child in get_child_collections():
        click.secho(child.name + "/", fg='blue')

    if current_collection is None:
        return

    for video in current_collection.get_videos().including_fields("name"):
        click.secho(video.name, fg='green')

    for image in current_collection.get_images().including_fields("name"):
        click.secho(image.name, fg='bright_green')

    file_fields = FieldsRequest()
    file_fields.include_field("file_locker_files.name")
    current_collection.populate(file_fields)
    for file in current_collection.file_locker_files:
        click.secho(file.name, fg='yellow')


@shell.command("files", help="List file locker files")
@click.option("-u", "--url", is_flag=True, help="If specified, also print a download URL")
def _files(url):
    if current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return

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
def _videos(size):
    if current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return
    
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
def _images():
    if current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return

    image_fields = FieldsRequest()
    image_fields.include_field("name")
    for image in current_collection.get_images(image_fields):
        click.echo(image.name)


@shell.command("open", help="Open in browser")
def _open():
    if pwd == '/':
        url = conservator.get_url()
    else:
        url = conservator.get_collection_url(current_collection)
    click.secho(f"Opening {url}...", fg='yellow')
    click.launch(url)


@shell.command(help="List child collection paths recursively")
def tree():
    collections = []
    if pwd == "/":
        for project in conservator.projects.all().including_fields("root_collection.path"):
            collections.append(project.root_collection)
    elif current_collection is None:
        click.secho("Not in a valid Collection", fg="red")
        return
    else:
        collections.append(current_collection)

    child_paths = FieldsRequest()
    child_paths.include_field("children.path")
    while len(collections) > 0:
        collection = collections.pop()
        click.echo(collection.path)
        collection.populate(child_paths)
        collections.extend(collection.children)


def run_shell_command(command):
    args = shlex.split(command)
    if len(args) == 0:
        return
    try:
        global ctx
        ctx = shell.make_context("$", args)
        shell.invoke(ctx)
    except click.exceptions.ClickException as e:
        click.secho(str(e), fg="red")
    except click.exceptions.Exit:
        pass
    except KeyboardInterrupt:
        click.secho("Interrupted", fg="red")


@click.command()
def interactive():
    global conservator
    conservator = Conservator.default()

    click.secho(
        """This is an interactive conservator "shell" that simulates the directory\n"""
        """structure of Conservator's collections. Type "help" to see available commands.""",
        fg="cyan")

    domain = conservator.get_domain()

    click.secho(f"Loading identity from {domain}...", fg="yellow")
    username = conservator.get_user().name
    get_root_collections()

    while True:
        user = click.style(f"{username}@{domain}:", fg='magenta', bold=True)
        path = click.style(f"{pwd}", fg='blue', bold=True)
        end = click.unstyle("$ ")
        command = input(user + path + end)
        run_shell_command(command)


if __name__ == "__main__":
    interactive()
