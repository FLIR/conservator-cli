import click

from conservator import Conservator, Credentials, QueryableCollection
from conservator.util import to_clean_string


def from_queryable_collection(name):
    @click.group(name=name)
    def g():
        pass


    @g.command()
    @click.argument('search_text')
    @click.option('-p', '--properties', default="", help="comma-separated list of properties to be displayed")
    def search(search_text, properties):
        # property names are separated by commas in --properties option
        properties = filter(lambda p: p != "", properties.split(","))

        conservator = Conservator(Credentials.default())
        collection = getattr(conservator, name)
        assert isinstance(collection, QueryableCollection)

        items = collection.search(search_text).with_fields(*properties)
        for item in items:
            click.echo(to_clean_string(item))

    @g.command()
    @click.argument('search_text', default="")
    def count(search_text):
        conservator = Conservator(Credentials.default())
        collection = getattr(conservator, name)
        assert isinstance(collection, QueryableCollection)

        click.echo(collection.count(search_text))

    return g


