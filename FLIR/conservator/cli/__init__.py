import click
from FLIR.conservator.config import Config
from FLIR.conservator.cli.managers import get_manager_command
from FLIR.conservator.cli.interactive import interactive
from FLIR.conservator.conservator import Conservator
from FLIR.conservator.generated import schema
from FLIR.conservator.managers import CollectionManager, DatasetManager, ProjectManager, VideoManager
from FLIR.conservator.util import to_clean_string
import logging


@click.group()
@click.option("--log", "--log-level",
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
              default="INFO", help="A logging level, from")
def main(log):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logging.basicConfig(level=levels[log])
    pass


@main.command(help="View or delete the current config")
@click.option('--delete', is_flag=True, help="If specified, delete the default credentials.")
def config(delete):
    if delete:
        Config.delete_saved_default_config()
        return
    default_config = Config.default()
    click.echo("Default config:")
    click.echo(f"  Email: {default_config.email}")
    click.echo(f"  Key: {default_config.key}")
    click.echo(f"  URL: {default_config.url}")


@main.command(help="Print information on the current user")
def whoami():
    conservator = Conservator.default()
    user = conservator.get_user()
    click.echo(to_clean_string(user))


main.add_command(get_manager_command(CollectionManager, schema.Collection, "collections"))
main.add_command(get_manager_command(DatasetManager, schema.Dataset, "datasets"))
main.add_command(get_manager_command(ProjectManager, schema.Project, "projects"))
main.add_command(get_manager_command(VideoManager, schema.Video, "videos"))
main.add_command(interactive)

if __name__ == "__main__":
    main()
