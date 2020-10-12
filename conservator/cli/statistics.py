import click
from conservator import Config, Conservator


@click.command(help="View the latest statistics of your conservator instance")
def stats():
    conservator = Conservator(Config.default())
    click.echo(conservator.stats)

