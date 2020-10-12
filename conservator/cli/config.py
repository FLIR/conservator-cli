import click
from conservator import Config, Conservator


@click.command(help="View or delete the current config")
@click.option('--delete', is_flag=True, help="If specified, delete the default credentials.")
def config(delete):
    if delete:
        Config.delete_saved_default_config()
        return
    config = Config.default()
    click.echo("Default config:")
    click.echo(f"  Email: {config.email}")
    click.echo(f"  Key: {config.key}")
    click.echo(f"  URL: {config.url}")
