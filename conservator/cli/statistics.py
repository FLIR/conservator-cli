import click
from conservator import Credentials, Conservator


@click.command()
def stats():
    conservator = Conservator(Credentials.default())
    click.echo(conservator.stats)

