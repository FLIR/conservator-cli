import click

from conservator.conservator import Conservator
from conservator.generated import schema
from conservator.managers import SearchableTypeManager
from conservator.managers.type_manager import TypeManager
from conservator.types import SearchableType
from conservator.util import to_clean_string


def from_manager_class(cls, name):
    singular_name = name[:-1] if name.endswith('s') else name

    def get_manager():
        conservator = Conservator.default()
        collection = getattr(conservator, name)
        assert isinstance(collection, cls)
        return collection

    @click.group(name=name, help=f"View or manage {name}")
    def g():
        pass

    if issubclass(cls, TypeManager):
        @g.command()
        def fields():
            o = getattr(schema, singular_name.capitalize())
            click.echo(f"Field names of {o}:")
            for field in o.__field_names__:
                click.echo(field)

        @g.command()
        @click.argument("id")
        @click.option("-p", "--properties", default="", help="If specified, a comma-separated list of properties to "
                                                             "be displayed. Otherwise, gets all properties.")
        def get(id, properties):
            properties = list(filter(lambda p: p != "", properties.split(",")))
            if len(properties) == 0:
                item = get_manager().get(idx=id, all_fields=True)
            else:
                item = get_manager().get(idx=id, fields=properties)
            click.echo(to_clean_string(item))

    if issubclass(cls, SearchableTypeManager):
        @g.command()
        @click.argument('search_text')
        @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
        def search(search_text, properties):
            # property names are separated by commas in --properties option
            properties = filter(lambda p: p != "", properties.split(","))

            items = get_manager().search(search_text).with_fields(*properties)
            for number, item in enumerate(items):
                click.echo(f"{singular_name.capitalize()} {number}:")
                click.echo(to_clean_string(item))

        @g.command(name="list")
        @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
        def list_(properties):            # property names are separated by commas in --properties option
            properties = filter(lambda p: p != "", properties.split(","))

            items = get_manager().all().with_fields(*properties)
            for number, item in enumerate(items):
                click.echo(f"{singular_name.capitalize()} {number}:")
                click.echo(to_clean_string(item))

        @g.command()
        @click.argument('search_text', default="")
        def count(search_text):
            click.echo(get_manager().count(search_text))

    return g


