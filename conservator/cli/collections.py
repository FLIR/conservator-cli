import click

from conservator import Conservator, Config, QueryableCollection
from conservator.generated import schema
from conservator.util import to_clean_string


def from_queryable_collection(name):
    @click.group(name=name)
    def g():
        pass

    singular_name = name[:-1] if name.endswith('s') else name

    @g.command()
    @click.argument('search_text')
    @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
    def search(search_text, properties):
        # property names are separated by commas in --properties option
        properties = filter(lambda p: p != "", properties.split(","))

        conservator = Conservator(Config.default())
        collection = getattr(conservator, name)
        assert isinstance(collection, QueryableCollection)

        items = collection.search(search_text).with_fields(*properties)
        for number, item in enumerate(items):
            click.echo(f"{singular_name.capitalize()} {number}:")
            click.echo(to_clean_string(item))

    @g.command()
    @click.argument('search_text', default="")
    def count(search_text):
        conservator = Conservator(Config.default())
        collection = getattr(conservator, name)
        assert isinstance(collection, QueryableCollection)

        click.echo(collection.count(search_text))

    @g.command()
    def fields():
        o = getattr(schema, singular_name.capitalize())
        click.echo(f"Field names of {o}:")
        for field in o.__field_names__:
            click.echo(field)

    return g


