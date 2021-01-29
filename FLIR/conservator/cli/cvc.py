import functools
import os
import subprocess

import click
import logging

from click import get_current_context

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.local_dataset import LocalDataset


class InvalidLocalDataset(Exception):
    def __init__(self, path):
        self.path = path


def pass_valid_local_dataset(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ops = get_current_context().obj
        if not os.path.exists(ops.index_path):
            raise InvalidLocalDataset(ops.path)
        return func(ops, *args, **kwargs)

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
    "-p", "--path", default=".", help="Path to dataset, defaults to current directory"
)
@click.pass_context
def main(ctx, log, path):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logging.basicConfig(level=levels[log])
    conservator = Conservator.default()
    ctx.obj = LocalDataset(conservator, path)


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
def clone(identifier, path, checkout):
    conservator = Conservator.default()
    dataset = conservator.datasets.from_string(identifier)
    cloned = LocalDataset.clone(dataset, path)
    if checkout is not None:
        cloned.checkout(checkout)


@main.command("checkout", help="Checkout a commit hash")
@click.argument("commit")
@pass_valid_local_dataset
def checkout_(local_dataset, commit):
    local_dataset.checkout(commit)


@main.command(help="Stage images for uploading and adding to index.json")
@click.argument("paths", type=click.Path(exists=True), nargs=-1)
@pass_valid_local_dataset
def add(local_dataset, paths):
    local_dataset.stage_local_images(paths)


@main.command(
    "commit",
    help="Commit changes to index.json and associated_files with the given message",
)
@click.argument("message")
@pass_valid_local_dataset
def commit_(local_dataset, message):
    local_dataset.add_local_changes()
    local_dataset.commit(message)


@main.command(help="Push commits")
@pass_valid_local_dataset
def push(local_dataset):
    local_dataset.push_commits()


@main.command(help="Pull the latest commits")
@pass_valid_local_dataset
def pull(local_dataset):
    click.echo("Updating index.json and associated files.")
    local_dataset.pull()
    click.echo("To download media, use cvc download.")


@main.command(help="Show changes in index.json and associated_files since last commit")
@pass_valid_local_dataset
def diff(local_dataset):
    subprocess.call(
        ["git", "diff", "index.json", "associated_files"], cwd=local_dataset.path
    )


@main.command("log", help="Show log of commits")
@pass_valid_local_dataset
def log_(local_dataset):
    subprocess.call(["git", "log"], cwd=local_dataset.path)


@main.command(help="Shows information on a specific commit or object")
@click.argument("hash", default=None, required=False)
@pass_valid_local_dataset
def show(local_dataset, hash):
    if hash is None:
        subprocess.call(["git", "show"], cwd=local_dataset.path)
    else:
        subprocess.call(["git", "show", hash], cwd=local_dataset.path)


@main.command(help="Print staged images and files")
@pass_valid_local_dataset
def status(local_dataset):
    subprocess.call(
        ["git", "status", "index.json", "associated_files"], cwd=local_dataset.path
    )
    images = local_dataset.get_staged_images()
    if len(images) == 0:
        click.echo("No images staged.")
        return

    for image_path in images:
        click.echo(f"Staged: {image_path}")
    click.echo("Use 'cvc upload' to upload these images and add them to index.json")


@main.command(help="Download media files from index.json")
@click.option("-a", "--include-analytics", is_flag=True)
@click.option(
    "-p",
    "--pool-size",
    type=int,
    default=10,
    help="Number of concurrent processes to use when downloading.",
)
@click.option(
    "-s",
    "--symlink",
    is_flag=True,
    help="If passed, use symlinks instead of hardlinks when linking cache and data.",
)
@pass_valid_local_dataset
def download(local_dataset, include_analytics, pool_size, symlink):
    local_dataset.download(
        include_analytics=include_analytics,
        include_eight_bit=True,
        process_count=pool_size,
        use_symlink=symlink,
    )


@main.command(help="Validate index.json format")
@pass_valid_local_dataset
def validate(local_dataset):
    if local_dataset.validate_index():
        click.secho("Valid", fg="green")
    else:
        click.secho("Invalid", fg="red")


@main.command(help="Upload staged images and add them to index.json")
@click.option(
    "--skip-copy",
    is_flag=True,
    help="If provided, skip copying images to the cache and /data directory",
)
@pass_valid_local_dataset
def upload(local_dataset, skip_copy):
    local_dataset.push_staged_images(copy_to_data=not skip_copy)


@main.command(
    help="Upload staged images (if any), then commit all changes to index.json "
    "and associated_files with message and push"
)
@click.argument("message")
@pass_valid_local_dataset
def publish(local_dataset, message):
    local_dataset.push_staged_images()
    local_dataset.add_local_changes()
    local_dataset.commit(message)
    local_dataset.push_commits()


@click.group(help="Commands for manipulating local datasets")
@click.option(
    "-p", "--path", default=".", help="Path to dataset, defaults to current directory"
)
@click.pass_context
def cvc(ctx, path):
    # This command is added to conservator CLI.
    # It is the same as main sans the log level stuff.
    # The conservator command handles logging, and would
    # result in confusing behavior if included twice.
    conservator = Conservator.default()
    ctx.obj = LocalDataset(conservator, path)


# Hacky way to "add" commands to both groups
cvc.commands = main.commands


if __name__ == "__main__":
    main()
