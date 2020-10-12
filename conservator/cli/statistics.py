import click
from conservator import Config, Conservator


@click.command()
def stats():
    conservator = Conservator(Config.default())
    click.echo(conservator.stats)

