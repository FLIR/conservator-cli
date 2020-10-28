import click
from conservator.config import Config


@click.command(help="View or delete the current config")
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
