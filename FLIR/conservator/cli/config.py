import json

import click

from FLIR.conservator.config import Config
from FLIR.conservator.conservator import Conservator


@click.group(name="config", help="Manage configs")
def config_():
    pass


@config_.command(help="Delete config")
@click.argument("name", default="default")
def delete(name):
    if click.confirm(
        "Are you sure? You can use conservator config edit to change individual values."
    ):
        Config.delete_saved_named_config(name)


@config_.command(help="View config")
@click.argument("name", default="default")
def view(name):
    config = Config.from_name(name)
    conservator = Conservator(config)
    click.echo(config)
    click.echo(f"Corresponds to email: {conservator.get_email()}")


@config_.command(name="list", help="List available config names")
def list_():
    for name in Config.saved_config_names():
        click.echo(name)


@config_.command(name="edit", help="Edit config")
@click.argument("name", default="default")
def edit_(name):
    config = Config.from_name(name)
    config_json = json.dumps(config.to_dict(), indent=2)
    value = click.edit(config_json)
    if value is not None:
        new_json = json.loads(value)
        new_config = Config.from_dict(new_json)
        new_config.save_to_named_config(name)
        click.echo(f"Edited {name}")
        return
    click.echo(f"No changes.")


@config_.command(name="set-default", help="Set default config")
@click.argument("name")
def set_default(name):
    config = Config.from_name(name)
    config.save_to_default_config()
    click.echo("Saved.")


@config_.command(help="Create a config")
@click.argument("name")
def create(name):
    config = Config.from_input()
    config.save_to_named_config(name)
