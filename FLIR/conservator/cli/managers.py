import click
import functools

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.managers import (
    SearchableTypeManager,
    CollectionManager,
    VideoManager,
    ImageManager,
    MediaTypeManager,
)


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
        if len(include) == 0:
            include = ("",)
        exclude = list(filter(lambda p: p != "", exclude.split(",")))
        f = FieldsRequest(include, exclude)
        kwargs["fields"] = f
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
            "-v", "--video-metadata", is_flag=True, help="Include video metadata"
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

    if issubclass(type_manager, VideoManager):

        @group.command(
            help="Download a video to the current directory, or the specified path."
        )
        @click.argument("id")
        @click.argument("path", default=".")
        @click.option(
            "-v", "--video-metadata", is_flag=True, help="Include video metadata"
        )
        @click.option(
            "-vo", "--video-metadata-only", is_flag=True, help="Only download metadata"
        )
        def download(id, path, video_metadata, video_metadata_only):
            video = get_instance().from_id(id)
            if video_metadata_only or video_metadata:
                video.download_metadata(path)
            if not video_metadata_only:
                video.download(path)

    if issubclass(type_manager, ImageManager):

        @group.command(
            help="Download an image to the current directory, or the specified path."
        )
        @click.argument("id")
        @click.argument("path", default=".")
        def download(id, path):
            image = get_instance().from_id(id)
            image.download(path)

    return group
