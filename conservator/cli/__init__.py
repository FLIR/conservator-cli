import click

from conservator.cli.collections import from_queryable_collection
from conservator.cli.config import config
from conservator.cli.statistics import stats


@click.group()
def main():
    # TODO: logging verbosity
    pass


main.add_command(stats)
main.add_command(config)
main.add_command(from_queryable_collection("videos"))
main.add_command(from_queryable_collection("datasets"))
main.add_command(from_queryable_collection("projects"))
main.add_command(from_queryable_collection("collections"))
