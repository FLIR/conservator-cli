import click

from conservator.cli.managers import from_manager_class
from conservator.cli.config import config
from conservator.cli.statistics import stats
from conservator.managers import VideosManager, DatasetsManager, ProjectsManager, CollectionsManager


@click.group()
def main():
    # TODO: logging verbosity
    pass


main.add_command(stats)
main.add_command(config)
main.add_command(from_manager_class(VideosManager, "videos"))
main.add_command(from_manager_class(DatasetsManager, "datasets"))
main.add_command(from_manager_class(ProjectsManager, "projects"))
main.add_command(from_manager_class(CollectionsManager, "collections"))
