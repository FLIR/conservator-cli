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
from FLIR.conservator.wrappers.collection import Collection, InvalidRemotePathException
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
        ctx_obj = click.get_current_context().obj
        conservator = Conservator.create(ctx_obj["config_name"])
        return type_manager(conservator)

    @click.group(name=name, help=f"View or manage {name}")
    def group():
        pass

    @group.command(name="fields", help=f"List the fields of a {sgqlc_type}")
    def fields_():
        click.echo(f"Field names of {sgqlc_type}:")
        field_names = sgqlc_type.__field_names__
        for field in field_names:
            click.echo(field)
        return field_names

    @group.command(
        help=f"Print a {sgqlc_type} from a unique identifier (ID, Path, Name, etc.)"
    )
    @click.argument("identifier")
    @fields_request
    def get(fields, identifier):
        item = get_instance().from_string(identifier)
        item.populate(fields)
        click.echo(item)
        return item

    if issubclass(type_manager, SearchableTypeManager):

        @group.command(help=f"Search for {sgqlc_type}s")
        @click.argument("search_text")
        @fields_request
        def search(fields, search_text):
            items = get_instance().search(search_text).with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)
            return items

        @group.command(name="list", help=f"List all {sgqlc_type}s")
        @fields_request
        def list_(fields):
            items = get_instance().all().with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)
            return items

        @group.command(
            help=f"Count all {sgqlc_type}s, or the number of {sgqlc_type}s returned in a search"
        )
        @click.argument("search_text", default="")
        def count(search_text):
            num_found = get_instance().count(search_text)
            click.echo(num_found)
            return num_found

    if issubclass(type_manager, CollectionManager):

        @group.command(help="Create a new collection with the given path.")
        @click.argument("collection_path")
        @click.option(
            "-p",
            "--parents",
            is_flag=True,
            help="Create all missing parent path components",
        )
        def create_path(collection_path, parents):
            cpath = collection_path
            if not cpath.startswith("/"):
                cpath = "/" + collection_path
            split_path = cpath.split("/")[1:]
            manager = get_instance()
            if len(split_path) > 1 and not parents:
                # Path is not a project.
                base_path = "/" + "/".join(split_path[:-1])
                # Unless parents is set, a missing base path is an error.
                try:
                    manager.from_remote_path(base_path)
                except InvalidRemotePathException:
                    click.echo(f"Base path {base_path} doesn't exist.")
                    click.echo("Specify '-p' to create all path components.")
                    return False
            try:
                collection = manager.from_remote_path(cpath)
                if collection:
                    click.echo(f"Path {cpath} already exists.")
                    return True
            except InvalidRemotePathException:
                pass
            Collection.create_from_remote_path(manager._conservator, cpath)
            return True

        @group.command(help="List media files contained in a given collection.")
        @click.argument("identifier")
        @click.option(
            "-r",
            "--recursive",
            is_flag=True,
            help="Include child collections recursively",
        )
        def list_media(identifier, recursive):
            manager = get_instance()
            collection_fields = FieldsRequest.create(("id", "name", "path"))
            top_collection = manager.from_string(identifier, collection_fields)
            media_fields = FieldsRequest.create(("id", "name"))
            if recursive:
                collection_paths = top_collection.recursively_get_children(
                    include_self=True, fields=collection_fields
                )
            else:
                collection_paths = [top_collection]
            no_results = True
            for coll in collection_paths:
                for media_file in coll.get_media(media_fields):
                    click.echo(f"{coll.path}/{media_file.name}")
                    no_results = False
            if no_results:
                click.echo(f"No media found in collection {identifier}")
            return True

        @group.command(
            help="Download a Collection to the current directory, or the specified path."
        )
        @click.argument("identifier")
        @click.argument("localpath", default=".")
        @click.option("-d", "--datasets", is_flag=True, help="Pull datasets")
        @click.option(
            "-v",
            "--video-metadata",
            is_flag=True,
            help="Include image and video metadata under subdir 'media_metadata/'",
        )
        @click.option(
            "-f",
            "--associated-files",
            is_flag=True,
            help="Include associated files under subdir 'associated_files/'",
        )
        @click.option(
            "-m", "--media", is_flag=True, help="Include media (videos and images)"
        )
        @click.option(
            "-p",
            "--preview_videos",
            is_flag=True,
            help="Download preview videos in place of full videos",
        )
        @click.option(
            "-r",
            "--recursive",
            is_flag=True,
            help="Include child collections recursively",
        )
        def download(
            identifier,
            localpath,
            datasets,
            video_metadata,
            associated_files,
            media,
            preview_videos,
            recursive,
        ):
            manager = get_instance()
            collection = manager.from_string(identifier)
            collection.download(
                localpath,
                datasets,
                video_metadata,
                associated_files,
                media,
                preview_videos,
                recursive,
            )
            return True

        @group.command(
            help="Upload a local directory to a Collection by ID or remote path"
        )
        @click.argument("identifier")
        @click.argument("localpath")
        @click.option(
            "-c",
            "--create-collection",
            is_flag=True,
            help="If identifier is a remote path that doesn't exist, attempt to create a collection at that path",
        )
        @click.option(
            "-v",
            "--video-metadata",
            is_flag=True,
            help="Include image and video metadata under subdir 'media_metadata/'",
        )
        @click.option(
            "-f",
            "--associated-files",
            is_flag=True,
            help="Include associated files under subdir 'associated_files/'",
        )
        @click.option(
            "-m", "--media", is_flag=True, help="Include media (videos and images)"
        )
        @click.option(
            "-r",
            "--recursive",
            is_flag=True,
            help="Include child directories recursively, creating collections as needed",
        )
        @click.option(
            "--resume-media",
            is_flag=True,
            help="Check if media files were previously uploaded, skip if so",
        )
        @click.option(
            "-n",
            "--max-retries",
            type=int,
            default=-1,
            help="max number of retries for uploading a media file (negative for infinite retries)",
        )
        def upload(
            identifier,
            localpath,
            video_metadata,
            associated_files,
            media,
            recursive,
            create_collection,
            resume_media,
            max_retries,
        ):
            manager = get_instance()
            if create_collection:
                collection = manager.from_remote_path(
                    identifier, make_if_no_exist=True, fields="id"
                )
            else:
                collection = manager.from_string(identifier)
            manager.upload(
                collection.id,
                localpath,
                video_metadata,
                associated_files,
                media,
                recursive,
                resume_media,
                max_retries,
            )
            return True

    if issubclass(type_manager, DatasetManager):

        @group.command(help="List a Dataset's commit history.")
        @click.argument("identifier")
        def history(identifier):
            dataset = get_instance().from_string(identifier)
            commit_fields = [
                "_id",
                "author_name",
                "author_email",
                "short_message",
                "parents",
                "tree",
            ]
            history = dataset.get_commit_history(fields=commit_fields)
            for commit in history:
                click.echo(to_clean_string(commit))
            return history

        @group.command(
            name="commit",
            help="View a specific Dataset commit. You can pass a commit hash, or a reference like HEAD~2.",
        )
        @click.argument("dataset_identifier")
        @click.argument("commit_id")
        def commit_(dataset_identifier, commit_id):
            dataset = get_instance().from_string(dataset_identifier)
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
            return commit

        @group.command(
            name="tree",
            help="List contents of a Dataset's version control tree. You can pass a tree hash, or a reference like HEAD.",
        )
        @click.argument("dataset_identifier")
        @click.argument("tree_id", default="HEAD")
        def tree_(dataset_identifier, tree_id):
            dataset = get_instance().from_string(dataset_identifier)
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
            return tree

        @group.command(
            name="blob", help="Download a blob from a Dataset's version control tree."
        )
        @click.argument("dataset_identifier")
        @click.argument("blob_id")
        @click.argument("path", default="blob")
        @click.option(
            "-b",
            "--browser",
            is_flag=True,
            help="If passed, perform the download using a browser.",
        )
        def blob(dataset_identifier, blob_id, path, browser):
            dataset = get_instance().from_string(dataset_identifier)
            if browser:
                blob_url = dataset.get_blob_url_by_id(blob_id)
                click.launch(blob_url)
                return
            dataset.download_blob(blob_id, path)
            return True

        @group.command(
            name="download-file",
            help="Download a Dataset's index.json or associated file. Defaults to latest commit.",
        )
        @click.argument("dataset_identifier")
        @click.argument("filename")
        @click.argument("path", default=".")
        @click.option("-c", "--commit-hash", default="HEAD")
        def download_file(dataset_identifier, filename, path, commit_hash):
            dataset = get_instance().from_string(dataset_identifier)
            dataset.download_blob_by_name(filename, path, commit_id=commit_hash)
            return True

        @group.command(
            name="download-index",
            help="Download a Dataset's index.json. Defaults to latest commit.",
        )
        @click.argument("dataset_identifier")
        @click.argument("path", default=".")
        @click.option("-c", "--commit-hash", default="HEAD")
        def download_index(dataset_identifier, path, commit_hash):
            dataset = get_instance().from_string(dataset_identifier)
            dataset.download_blob_by_name("index.json", path, commit_id=commit_hash)
            return True

    if issubclass(type_manager, MediaTypeManager):

        @group.command(help="Upload a media file to collection")
        @click.argument("localpath", default=".")
        @click.argument("remote_collection", default=".")
        @click.option(
            "-r",
            "--remote-name",
            help="If specified, the name of the remote media. Defaults to the local file name",
        )
        @click.option(
            "-c",
            "--create-collections",
            is_flag=True,
            help="If given and a remote path is provided, collections will be created to reach the remote path",
        )
        def upload(localpath, remote_collection, remote_name, create_collections):
            ctx_obj = click.get_current_context().obj
            conservator = Conservator.create(ctx_obj["config_name"])
            if create_collections:
                collection = conservator.collections.from_remote_path(
                    path=remote_collection, make_if_no_exist=True, fields="id"
                )
            else:
                collection = conservator.collections.from_string(
                    remote_collection, fields="id"
                )
            conservator.media.upload(
                localpath, collection=collection, remote_name=remote_name
            )
            return True

        @group.command(
            help="Download media to the current directory, or the specified path."
        )
        @click.argument("identifier")
        @click.argument("path", default=".")
        @click.option("-m", "--metadata", is_flag=True, help="Include metadata")
        @click.option(
            "-mo", "--metadata-only", is_flag=True, help="Only download metadata"
        )
        def download(identifier, path, metadata, metadata_only):
            media = get_instance().from_string(identifier)
            if metadata_only or metadata:
                media.download_metadata(path)
            if not metadata_only:
                media.download(path)
            return True

    return group
