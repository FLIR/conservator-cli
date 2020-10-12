import click

from conservator import Conservator, Config, QueryableCollection
from conservator.generated import schema
from conservator.util import to_clean_string


def from_queryable_collection(name):
    def get_collection():
        conservator = Conservator(Config.default())
        collection = getattr(conservator, name)
        assert isinstance(collection, QueryableCollection)
        return collection

    @click.group(name=name, help=f"Search and view details about {name}")
    def g():
        pass

    singular_name = name[:-1] if name.endswith('s') else name

    @g.command()
    @click.argument('search_text')
    @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
    def search(search_text, properties):
        # property names are separated by commas in --properties option
        properties = filter(lambda p: p != "", properties.split(","))

        items = get_collection().search(search_text).with_fields(*properties)
        for number, item in enumerate(items):
            click.echo(f"{singular_name.capitalize()} {number}:")
            click.echo(to_clean_string(item))

    @g.command()
    @click.argument('search_text', default="")
    def count(search_text):
        click.echo(get_collection().count(search_text))

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
            item = get_collection().get(idx=id, all_fields=True)
        else:
            item = get_collection().get(idx=id, fields=properties)
        click.echo(to_clean_string(item))

    @g.command(name="list")
    @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
    def list_(properties):
        properties = filter(lambda p: p != "", properties.split(","))

        items = get_collection().all().with_fields(*properties)
        for number, item in enumerate(items):
            click.echo(f"{singular_name.capitalize()} {number}:")
            click.echo(to_clean_string(item))

    return g


