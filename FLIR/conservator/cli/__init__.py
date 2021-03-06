import click

from FLIR.conservator.cli.config import config_
from FLIR.conservator.cli.managers import get_manager_command
from FLIR.conservator.cli.interactive import interactive
from FLIR.conservator.config import Config
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
    default=None,
    help="Conservator config name, use default credentials if not specified",
)
def main(log, config):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logging.basicConfig(level=levels[log])

    conservator = Conservator.create(config_name=config)
    ctx = click.get_current_context()
    ctx.ensure_object(dict)
    ctx.obj["conservator"] = conservator


@main.command(help="Print information on the current user")
def whoami():
    ctx_obj = click.get_current_context().obj
    conservator = ctx_obj["conservator"]
    user = conservator.get_user()
    click.echo(to_clean_string(user))


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
