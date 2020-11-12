import click

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.managers import SearchableTypeManager


def get_manager_command(type_manager, sgqlc_type, name, singular_name):
    def get_instance():
        conservator = Conservator.default()
        return type_manager(conservator)

    @click.group(name=name, help=f"View or manage {name}")
    def group():
        pass

    @group.command()
    def fields():
        click.echo(f"Field names of {sgqlc_type}:")
        for field in sgqlc_type.__field_names__:
            click.echo(field)

    @group.command()
    @click.argument("id")
    @click.option("-p", "--properties", default="", help="If specified, a comma-separated list of properties to "
                                                         "be displayed. Otherwise, gets all properties.")
    def get(id, properties):
        properties = list(filter(lambda p: p != "", properties.split(",")))
        item = get_instance().from_id(id)
        if len(properties) == 0:
            item.populate_all()
        else:
            item.populate(properties)
        click.echo(item)

    if issubclass(type_manager, SearchableTypeManager):
        @group.command()
        @click.argument('search_text')
        @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
        def search(search_text, properties):
            # property names are separated by commas in --properties option
            properties = filter(lambda p: p != "", properties.split(","))

            items = get_instance().search(search_text).including_fields(*properties)
            for number, item in enumerate(items):
                click.echo(f"{name.capitalize()} {number}:")
                click.echo(item)

        @group.command(name="list")
        @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
        def list_(properties):            # property names are separated by commas in --properties option
            properties = filter(lambda p: p != "", properties.split(","))

            items = get_instance().all().including_fields(*properties)
            for number, item in enumerate(items):
                click.echo(f"{singular_name.capitalize()} {number}:")
                click.echo(item)

        @group.command()
        @click.argument('search_text', default="")
        def count(search_text):
            click.echo(get_instance().count(search_text))

    return group

