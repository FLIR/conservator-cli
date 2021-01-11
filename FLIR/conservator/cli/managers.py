import os

import click
import functools

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.managers import (
    SearchableTypeManager,
    CollectionManager,
    MediaTypeManager,
    DatasetManager,
)
from FLIR.conservator.util import to_clean_string


def fields_request(func):
    @click.option(
        "-i",
        "-p",
        "--properties",
        default="",
        help="If specified, a comma-separated list of properties to "
        "be displayed. Otherwise, gets all properties.",
    )
    @click.option(
        "-e",
        "--exclude",
        default="",
        help="If specified, a comma-separated list of properties to "
        "be excluded, overriding the included properties.",
    )
    @functools.wraps(func)
    def wrapper(properties="", exclude="", **kwargs):
        include = list(filter(lambda p: p != "", properties.split(",")))
        exclude = list(filter(lambda p: p != "", exclude.split(",")))
        fields = {name: True for name in include}
        fields.update(**{name: False for name in exclude})
        kwargs["fields"] = FieldsRequest.create(fields)
        return func(**kwargs)

    return wrapper


def get_manager_command(type_manager, sgqlc_type, name):
    def get_instance():
        conservator = Conservator.default()
        return type_manager(conservator)

    @click.group(name=name, help=f"View or manage {name}")
    def group():
        pass

    @group.command(name="fields", help=f"List the fields of a {sgqlc_type}")
    def fields_():
        click.echo(f"Field names of {sgqlc_type}:")
        for field in sgqlc_type.__field_names__:
            click.echo(field)

    @group.command(help=f"Print a {sgqlc_type} from an ID")
    @click.argument("id")
    @fields_request
    def get(fields, id):
        item = get_instance().from_id(id)
        item.populate(fields)
        click.echo(item)

    if issubclass(type_manager, SearchableTypeManager):

        @group.command(help=f"Search for {sgqlc_type}s")
        @click.argument("search_text")
        @fields_request
        def search(fields, search_text):
            items = get_instance().search(search_text).with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)

        @group.command(name="list", help=f"List all {sgqlc_type}s")
        @fields_request
        def list_(fields):
            items = get_instance().all().with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)

        @group.command(
            help=f"Count all {sgqlc_type}s, or the number of {sgqlc_type}s returned in a search"
        )
        @click.argument("search_text", default="")
        def count(search_text):
            click.echo(get_instance().count(search_text))

    if issubclass(type_manager, CollectionManager):

        @group.command(
            help="Download a collection to the current directory, or the specified path."
        )
        @click.argument("id")
        @click.argument("path", default=".")
        @click.option("-d", "--datasets", is_flag=True, help="Pull datasets")
        @click.option(
            "-v",
            "--video-metadata",
            is_flag=True,
            help="Include image and video metadata",
        )
        @click.option(
            "-f", "--associated-files", is_flag=True, help="Include associated files"
        )
        @click.option(
            "-m", "--media", is_flag=True, help="Include media (videos and images)"
        )
        @click.option(
            "-r",
            "--recursive",
            is_flag=True,
            help="Include child collections recursively",
        )
        def download(
            id, path, datasets, video_metadata, associated_files, media, recursive
        ):
            collection = get_instance().from_id(id)
            collection.download(
                path, datasets, video_metadata, associated_files, media, recursive
            )

    if issubclass(type_manager, DatasetManager):

        @group.command(help="List a Dataset's commit history.")
        @click.argument("id")
        def history(id):
            dataset = get_instance().from_id(id)
            commit_fields = [
                "_id",
                "author_name",
                "author_email",
                "short_message",
                "parents",
                "tree",
            ]
            for commit in dataset.get_commit_history(fields=commit_fields):
                click.echo(to_clean_string(commit))

        @group.command(
            name="commit",
            help="View a specific Dataset commit. You can pass a commit hash, or a reference like HEAD~2.",
        )
        @click.argument("dataset_id")
        @click.argument("commit_id")
        def commit_(dataset_id, commit_id):
            dataset = get_instance().from_id(dataset_id)
            commit_fields = [
                "_id",
                "author_name",
                "author_email",
                "short_message",
                "parents",
                "tree",
            ]
            commit = dataset.get_commit_by_id(commit_id, fields=commit_fields)
            click.echo(to_clean_string(commit))

        @group.command(
            name="tree",
            help="List contents of a Dataset's version control tree. You can pass a tree hash, or a reference like HEAD.",
        )
        @click.argument("dataset_id")
        @click.argument("tree_id", default="HEAD")
        def tree_(dataset_id, tree_id):
            dataset = get_instance().from_id(dataset_id)
            tree_fields = [
                "size",
                "tree_list._id",
                "tree_list.type",
                "tree_list.name",
                "tree_list.mode",
                "tree_list.size",
            ]
            tree = dataset.get_tree_by_id(tree_id, fields=tree_fields)
            click.echo(f"Tree {tree_id} (size: {tree.size})")
            click.echo(f"  Type\tName\tHash")
            for item in tree.tree_list:
                click.echo(f"  {item.type}\t{item.name}\t{item._id}")

        @group.command(
            name="blob", help="Download a blob from a Dataset's version control tree."
        )
        @click.argument("dataset_id")
        @click.argument("blob_id")
        @click.argument("path", default="./blob")
        @click.option(
            "-b",
            "--browser",
            is_flag=True,
            help="If passed, perform the download using a browser.",
        )
        def blob(dataset_id, blob_id, path, browser):
            dataset = get_instance().from_id(dataset_id)
            if browser:
                blob_url = dataset.get_blob_url_by_id(blob_id)
                click.launch(blob_url)
                return
            dataset.download_blob(blob_id, path)

        @group.command(
            name="download-file",
            help="Download a Dataset's index.json or associated file. Defaults to latest commit.",
        )
        @click.argument("dataset_id")
        @click.argument("filename")
        @click.argument("path", default=".")
        @click.option("-c", "--commit-hash", default="HEAD")
        def download_file(dataset_id, filename, path, commit_hash):
            dataset = get_instance().from_id(dataset_id)
            dataset.download_blob_by_name(filename, path, commit_id=commit_hash)

        @group.command(
            name="download-index",
            help="Download a Dataset's index.json. Defaults to latest commit.",
        )
        @click.argument("dataset_id")
        @click.argument("path", default=".")
        @click.option("-c", "--commit-hash", default="HEAD")
        def download_index(dataset_id, path, commit_hash):
            dataset = get_instance().from_id(dataset_id)
            dataset.download_blob_by_name("index.json", path, commit_id=commit_hash)

    if issubclass(type_manager, MediaTypeManager):

        @group.command(help="Upload a media file to collection")
        @click.argument("localpath", default=".")
        @click.argument("remotepath", default=".")
        @click.option(
            "-r",
            "--remote-name",
            help="If specified, the name of the remote media. Defaults to the local file name",
        )
        @click.option(
            "-c",
            "--create-collections",
            is_flag=True,
            help="If given, collections will be created to reach the remote path",
        )
        def upload(localpath, remotepath, remote_name, create_collections):
            i = get_instance()
            collection = i._conservator.collections.from_remote_path(
                remotepath, make_if_no_exist=create_collections
            )
            i.upload(localpath, collection=collection, remote_name=remote_name)

        @group.command(
            help="Download media to the current directory, or the specified path."
        )
        @click.argument("id")
        @click.argument("path", default=".")
        @click.option("-m", "--metadata", is_flag=True, help="Include metadata")
        @click.option(
            "-mo", "--metadata-only", is_flag=True, help="Only download metadata"
        )
        def download(id, path, metadata, metadata_only):
            media = get_instance().from_id(id)
            if metadata_only or metadata:
                media.download_metadata(path)
            if not metadata_only:
                media.download(path)

    return group
