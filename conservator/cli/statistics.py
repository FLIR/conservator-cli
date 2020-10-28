import click
from conservator import Conservator


@click.command(help="View the latest statistics of your conservator instance")
def stats():
    conservator = Conservator.default()
    click.echo(conservator.stats)

