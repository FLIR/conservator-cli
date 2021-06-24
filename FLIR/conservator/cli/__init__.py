import click
import subprocess

from FLIR.conservator.cli.config import config_
from FLIR.conservator.cli.managers import get_manager_command
from FLIR.conservator.cli.interactive import interactive
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated import schema
from FLIR.conservator.managers import (
    CollectionManager,
    DatasetManager,
    ProjectManager,
    VideoManager,
    ImageManager,
)
from FLIR.conservator.util import to_clean_string
from FLIR.conservator.cli.cvc import cvc
import logging
import requests
import json
import pip


@click.group()
@click.option(
    "--log",
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level, defaults to INFO",
)
@click.option(
    "--config",
    default="default",
    help="Conservator config name, use default credentials if not specified",
)
@click.version_option(prog_name="conservator-cli", package_name="conservator-cli")
def main(log, config):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logging.basicConfig(level=levels[log])

    ctx = click.get_current_context()
    ctx.ensure_object(dict)
    ctx.obj["config_name"] = config


@main.command(help="Print information on the current user")
def whoami():
    ctx_obj = click.get_current_context().obj
    conservator = Conservator.create(ctx_obj["config_name"])
    user = conservator.get_user()
    click.echo(to_clean_string(user))


@main.command(help="Print whether or not an update is available")
def checkUpdate():
    url = "https://pypi.org/pypi/conservator-cli/json"
    response = requests.get(url).text
    current_version = json.loads(response)["info"]["version"]
    data = json.loads(subprocess.check_output(["pip", "list", "--format", "json"]))
    local_version = [
        package for package in data if package["name"] == "conservator-cli"
    ][0]["version"]
    print("local_version:", local_version)
    print("current_version:", current_version)
    # compare local and remote versions
    if local_version != current_version:
        click.echo("Newer version of conservator-cli available")
    else:
        click.echo("No update for conservator-cli available")


main.add_command(config_)
main.add_command(
    get_manager_command(CollectionManager, schema.Collection, "collections")
)
main.add_command(get_manager_command(DatasetManager, schema.Dataset, "datasets"))
main.add_command(get_manager_command(ProjectManager, schema.Project, "projects"))
main.add_command(get_manager_command(VideoManager, schema.Video, "videos"))
main.add_command(get_manager_command(ImageManager, schema.Image, "images"))
main.add_command(interactive)
main.add_command(cvc, name="cvc")

if __name__ == "__main__":
    main()
