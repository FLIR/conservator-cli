# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=broad-except
import functools
import os
import subprocess
import sys
import configparser
import logging

from urllib import parse

import click

from click import get_current_context

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.local_dataset import LocalDataset
from FLIR.conservator.util import check_platform, check_dir_access


def pass_valid_local_dataset(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx_obj = get_current_context().obj

        if "conservator" in ctx_obj:
            conservator = ctx_obj["conservator"]
        elif "url" in ctx_obj and "api_key" in ctx_obj:
            path = ctx_obj["cvc_local_path"]
            config_dict = {
                "CONSERVATOR_URL": ctx_obj["url"],
                "CONSERVATOR_API_KEY": ctx_obj["api_key"],
            }
            conservator = Conservator.from_config_dict(config_dict)
            ctx_obj["conservator"] = conservator
        else:
            path = ctx_obj["cvc_local_path"]
            conservator = Conservator.create(ctx_obj["config_name"])
            ctx_obj["conservator"] = conservator

        # raises InvalidLocalDatasetPath if the path does not point to a
        # valid LocalDataset (defined as a directory containing index.json).
        local_dataset = LocalDataset(conservator, path)

        return func(local_dataset, *args, **kwargs)

    return wrapper


def check_git_config(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx_obj = get_current_context().obj

        if "conservator" in ctx_obj:
            conservator = ctx_obj["conservator"]
        else:
            path = ctx_obj["cvc_local_path"]
            conservator = Conservator.create(ctx_obj["config_name"])
            ctx_obj["conservator"] = conservator

        logging.disable(logging.CRITICAL)

        try:
            conservator.get_email()
        except Exception:
            click.echo(
                "Cannot retrieve user details! Please check your API key configuration"
            )
            sys.exit(1)

        logging.disable(logging.NOTSET)

        path = ctx_obj["cvc_local_path"]
        full_path = os.path.join(os.getcwd(), path)
        git_config_file = os.path.join(full_path, ".git", "config")

        if not os.path.exists(git_config_file):
            click.echo(f"Dataset git config file ({git_config_file}) is missing!")
            sys.exit(1)

        git_config = configparser.RawConfigParser()

        git_config.read(git_config_file)

        git_url = git_config.get('remote "origin"', "url")

        git_url = parse.unquote(git_url)

        split_result = parse.urlsplit(git_url)

        host_name = f"{split_result.scheme}://{split_result.hostname}"

        if split_result.port is not None:
            host_name = f"{host_name}:{split_result.port}"

        if not conservator.get_email() == split_result.username:
            click.echo(
                f"This dataset was checked out as {split_result.username},\
                    not {conservator.get_email()}!"
            )
            click.echo("Run ", nl=False)
            click.echo(click.style("conservator config view", bold=True), nl=False)
            click.echo(" to see your current configuration")
            click.echo("Run ", nl=False)
            click.echo(click.style("cvc update-identity", bold=True), nl=False)
            click.echo(" to update the configuration of the current dataset")
            sys.exit(1)

        if conservator.get_url() != host_name:
            click.echo(
                f"This dataset was checked out from {host_name}, not {conservator.get_url()}!"
            )
            click.echo("Run ", nl=False)
            click.echo(click.style("conservator config view", bold=True), nl=False)
            click.echo(" to see your current configuration")
            sys.exit(1)

        if conservator.config.key != split_result.password:
            click.echo(
                "Your currently configured API key does not match\
                    the API key used to check out this dataset"
            )
            click.echo("Run ", nl=False)
            click.echo(click.style("conservator config view", bold=True), nl=False)
            click.echo(" to see your current configuration")
            click.echo("Run ", nl=False)
            click.echo(click.style("cvc update-identity", bold=True), nl=False)
            click.echo(" to update the configuration of the current dataset")
            sys.exit(1)

        return func(*args, **kwargs)

    return wrapper


@click.group(help="Commands for manipulating local datasets")
@click.option(
    "--log",
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level, defaults to INFO",
)
@click.option(
    "--config",
    default=None,
    help="Conservator config name, use default credentials if not specified",
)
@click.option(
    "-p", "--path", default=".", help="Path to dataset, defaults to current directory"
)
@click.option("-u", "--url", help="URL of Conservator instance to connect to")
@click.option("-k", "--api-key", help="API Key to use when connecting to Conservator")
@click.version_option(prog_name="conservator-cli", package_name="conservator-cli")
@click.pass_context
def main(ctx, log, path, config, url, api_key):
    check_platform()
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logging.basicConfig(level=levels[log])

    ctx.ensure_object(dict)
    ctx.obj["config_name"] = config
    ctx.obj["cvc_local_path"] = path
    if url is None and api_key is not None:
        click.secho("Must provide either both url and api_key, or neither!", fg="red")
        sys.exit(1)
    if url is not None and api_key is None:
        click.secho("Must provide either both url and api_key, or neither!", fg="red")
        sys.exit(1)
    if url is not None:
        ctx.obj["url"] = url
    if api_key is not None:
        ctx.obj["api_key"] = api_key


@main.command(help="Clone a dataset by id, path, or name (if unique)")
@click.argument("identifier")
@click.option(
    "-p",
    "--path",
    default=None,
    help="An empty directory to clone the dataset to. Defaults to a new "
    "directory with the name of the dataset",
)
@click.option(
    "-c", "--checkout", help="If specified, a commit hash to checkout after cloning"
)
@click.option("-u", "--url", help="URL of Conservator instance to connect to")
@click.option("-k", "--api-key", help="API Key to use when connecting to Conservator")
@click.pass_context
def clone(ctx, identifier, path, checkout, url, api_key):
    if not check_dir_access(os.getcwd()):
        click.secho(f"Cannot clone to directory {os.getcwd()}!", fg="red", bold=True)
        sys.exit(1)
    if url is not None and api_key is not None:
        config_dict = {"CONSERVATOR_URL": url, "CONSERVATOR_API_KEY": api_key}
        conservator = Conservator.from_config_dict(config_dict)
    else:
        conservator = Conservator.create(ctx.obj["config_name"])
    dataset = conservator.datasets.from_string(identifier)
    cloned = LocalDataset.clone(dataset, path)
    if checkout is not None:
        cloned.checkout(checkout)


@main.command("checkout", help="Checkout a commit hash")
@click.argument("commit")
@pass_valid_local_dataset
@check_git_config
def checkout_(local_dataset, commit):
    local_dataset.checkout(commit)


# pylint: disable=unused-argument
def is_image_file(ctx, param, value):
    for filename in value:
        if not LocalDataset.get_image_info(filename):
            raise click.BadParameter(
                f"{filename} is not an image -- use 'cvc publish' to add associated files"
            )
    return value


@main.command("stage-image", help="Stage images for uploading")
@click.argument("paths", type=click.Path(exists=True), callback=is_image_file, nargs=-1)
@pass_valid_local_dataset
@check_git_config
def stage_image(local_dataset, paths):
    if len(paths) == 0:
        click.echo("No images to stage!")
        return
    new_image_count = local_dataset.stage_local_images(paths)
    click.echo(f"{new_image_count} images staged for upload")


@main.command("unstage-image", help="Un-stage images for uploading")
@click.argument("paths", type=click.Path(exists=True), callback=is_image_file, nargs=-1)
@pass_valid_local_dataset
@check_git_config
def unstage_image(local_dataset, paths):
    local_dataset.unstage_local_images(paths)


@main.command(
    "commit",
    help="Commit changes to JSONL or index.json and associated_files with the given message",
)
@click.argument("message")
@click.option(
    "--skip-validation", is_flag=True, help="Skip frames.jsonl / index.json validation."
)
@pass_valid_local_dataset
@check_git_config
def commit_(local_dataset, message, skip_validation):
    local_dataset.add_local_changes(skip_validation=skip_validation)
    local_dataset.commit(message)


@main.command(help="Push commits")
@pass_valid_local_dataset
@check_git_config
def push(local_dataset):
    local_dataset.push_commits()


@main.command(help="Pull the latest commits")
@pass_valid_local_dataset
@check_git_config
def pull(local_dataset):
    click.echo("Updating JSONL, index.json and associated files.")
    local_dataset.pull()
    click.echo("To download media, use cvc download.")


@main.command(
    help="Show changes in JSONL, index.json and associated_files since last commit"
)
@pass_valid_local_dataset
@check_git_config
def diff(local_dataset):
    subprocess.call(
        ["git", "diff", "*.jsonl", "index.json", "associated_files"],
        cwd=local_dataset.path,
    )


@main.command("log", help="Show log of commits")
@pass_valid_local_dataset
@check_git_config
def log_(local_dataset):
    subprocess.call(["git", "log"], cwd=local_dataset.path)


@main.command(help="Shows information on a specific commit or object")
@click.argument("hash", default=None, required=False)
@pass_valid_local_dataset
@check_git_config
def show(local_dataset, hash):
    if hash is None:
        subprocess.call(["git", "show"], cwd=local_dataset.path)
    else:
        subprocess.call(["git", "show", hash], cwd=local_dataset.path)


@main.command(help="Print staged images and files")
@pass_valid_local_dataset
@check_git_config
def status(local_dataset):
    subprocess.call(
        ["git", "status", "*.jsonl", "index.json", "associated_files"],
        cwd=local_dataset.path,
    )
    images = local_dataset.get_staged_images()
    if len(images) == 0:
        click.echo("No images staged.")
        return

    for image_path in images:
        click.echo(f"Staged: {image_path}")
    click.echo(
        "Use 'cvc upload-images' to upload these images and add them to frames.jsonl or index.json"
    )


@main.command(help="Download media files from frames.jsonl or index.json")
@click.option(
    "-r", "--include-raw", is_flag=True, help="Include raw TIFF images, if available"
)
@click.option(
    "-a", "--include-analytics", is_flag=True, help="Deprecated; use -r option instead"
)
@click.option(
    "-p",
    "--pool-size",
    type=int,
    default=10,
    show_default=True,
    help="Number of concurrent processes to use when downloading.",
)
@click.option(
    "-s",
    "--symlink",
    is_flag=True,
    help="If passed, use symlinks instead of hardlinks when linking cache and data.",
)
@click.option(
    "-t",
    "--tries",
    type=int,
    default=5,
    show_default=True,
    help="Number of tries to recover from spurious server errors.",
)
@pass_valid_local_dataset
@check_git_config
def download(local_dataset, include_raw, include_analytics, pool_size, symlink, tries):
    if include_raw and not check_dir_access(local_dataset.data_path):
        click.secho(f"Cannot write to {local_dataset.data_path}!", fg="red", bold=True)
        sys.exit(1)

    if include_analytics and not check_dir_access(local_dataset.raw_data_path):
        click.secho(f"Cannot write to {local_dataset.data_path}!", fg="red", bold=True)
        sys.exit(1)

    if not check_dir_access(local_dataset.cache_path):
        click.secho(
            f"Cannot write to cache directory ({local_dataset.cache_path})!",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    if pool_size == 10:  # default
        yellow = "\x1b[33;21m"
        cyan = "\x1b[36;21m"
        reset = "\x1b[0m"
        click.echo(
            f"{yellow}If you have a fast connection, you might be able to speed "
            f"this up by rerunning with the -p (--process_count) option. "
            f"For instance: {cyan}cvc download -p 50{reset}"
        )
    if include_analytics:
        click.echo("The -a option has been deprecated; please use -r instead.")
    download_status = None
    try:
        download_status = local_dataset.download(
            include_raw=include_raw or include_analytics,
            include_eight_bit=True,
            process_count=pool_size,
            use_symlink=symlink,
            tries=tries,
        )
    except OSError as exc:
        if exc.errno == 18:
            red = "\x1B[31m"
            reset = "\x1b[0m"
            click.echo(
                f"  {red}Error - Conservator cache directory (cache_dir) is on a different \
volume, and cannot be used.{reset}"
            )
            click.echo(
                f"  {red}Either use the -s/--symlink flag with cvc download, or move your cache \
directory to the same volume the dataset is on."
            )
            click.echo(
                f"  {red}See \
https://flir.github.io/conservator-cli/usage/cvc_guide.html#downloading-frames \
for details.{reset}"
            )
            sys.exit(1)

        raise OSError from exc
    if not download_status:
        sys.exit(1)


@main.command(help="Validate index.json and frames.jsonl formats")
@pass_valid_local_dataset
@check_git_config
@click.option(
    "--skip_index",
    is_flag=True,
    help="If provided, only validate frames.jsonl if present",
)
def validate(local_dataset, skip_index):
    if not skip_index:
        if local_dataset.validate_index():
            click.secho("index.json Valid", fg="green")
        else:
            click.secho("index.json Invalid", fg="red")

    if os.path.exists(local_dataset.frames_path):
        if local_dataset.validate_jsonl():
            click.secho("JSONL Files Valid", fg="green")
        else:
            click.secho("JSONL Files Invalid", fg="red")
    elif skip_index:
        click.echo("No .jsonl files found.")


@main.command(
    "upload-images",
    help="Upload staged images and add them to frames.jsonl or index.json",
)
@click.option(
    "--skip-copy",
    is_flag=True,
    help="If provided, skip copying images to the cache and /data directory",
)
@click.option(
    "-t",
    "--tries",
    type=int,
    default=5,
    show_default=True,
    help="Number of tries to recover from spurious server errors.",
)
@pass_valid_local_dataset
@check_git_config
def upload_images(local_dataset, skip_copy, tries):
    new_frame_count = local_dataset.push_staged_images(
        copy_to_data=not skip_copy, tries=tries
    )
    file_name = "index.json"
    if not local_dataset.is_index_usable():
        file_name = "frames.jsonl"
    click.echo(
        f"Uploaded {new_frame_count} images and added {new_frame_count} frames to {file_name}"
    )


@main.command(
    help="Upload staged images (if any), commit all changes to metadata "
    "(frames.jsonl or index.json) and/or associated files (files inside associated_files/), "
    "and push to server with given message. "
    "Note that associated files can be added by putting them into associated_files/ subdir "
    "before running 'publish'."
)
@click.argument("message")
@click.option(
    "--skip-validation", is_flag=True, help="Skip JSONL / index.json validation."
)
@click.option(
    "-t",
    "--tries",
    type=int,
    default=5,
    show_default=True,
    help="Number of tries to recover from spurious server errors.",
)
@pass_valid_local_dataset
@check_git_config
def publish(local_dataset, message, skip_validation, tries):
    local_dataset.push_staged_images(tries=tries)
    local_dataset.add_local_changes(skip_validation=skip_validation)
    local_dataset.commit(message)
    local_dataset.push_commits()


@main.command(
    "update-identity",
    help="Updates the configuration of the selected dataset\
        to match current conservator-cli configuration",
)
@pass_valid_local_dataset
def update_identity(local_dataset):
    ctx_obj = get_current_context().obj
    conservator = Conservator.create(ctx_obj["config_name"])

    path = ctx_obj["cvc_local_path"]
    full_path = os.path.join(os.getcwd(), path)
    git_config_file = os.path.join(full_path, ".git", "config")

    if not os.path.exists(git_config_file):
        click.echo(f"Dataset git config file ({git_config_file}) is missing!")
        sys.exit(1)

    git_config = configparser.RawConfigParser()

    git_config.read(git_config_file)

    git_url = git_config.get('remote "origin"', "url")

    git_url = parse.unquote(git_url)

    split_result = parse.urlsplit(git_url)

    new_url = f"{conservator.get_authenticated_url()}{split_result.path}"

    git_config.set('remote "origin"', "url", new_url)

    git_config.set("user", "email", conservator.email)

    with open(git_config_file, "w", encoding="UTF-8") as config_file:
        git_config.write(config_file)
        click.echo(f"Updated config file {git_config_file}")


@main.command(
    "add",
    help="Deprecated; use stage-image instead.",
)
@click.argument("paths", type=click.Path(exists=True), nargs=-1, required=False)
def add(paths):
    click.echo("Deprecated; use stage-image instead.")


@main.command(
    "upload",
    help="Deprecated; use upload-images instead.",
)
@click.option(
    "--skip-copy",
    is_flag=True,
    required=False,
)
@click.option(
    "-t",
    "--tries",
    type=int,
    default=5,
    required=False,
)
def upload(skip_copy, tries):
    click.echo("Deprecated; use upload-images instead.")


@click.group(help="Commands for manipulating local datasets")
@click.option(
    "-p", "--path", default=".", help="Path to dataset, defaults to current directory"
)
@click.pass_context
def cvc(ctx, path):
    # This command is added to conservator CLI.
    # It is the same as main() except it skips things that toplevel
    # conservator command already handles (logging and conservator config,
    # and would result in confusing behavior if included twice.
    check_platform()
    ctx.obj["cvc_local_path"] = path


# Hacky way to "add" commands to both groups
cvc.commands = main.commands

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
