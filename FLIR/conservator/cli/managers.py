import click
import functools

from FLIR.conservator.conservator import Conservator
from FLIR.conservator.fields_request import FieldsRequest
from FLIR.conservator.managers import SearchableTypeManager


def fields_request(func):
    @click.option("-i", "-p", "--properties", default="", help="If specified, a comma-separated list of properties to "
                                                         "be displayed. Otherwise, gets all properties.")
    @click.option("-e", "--exclude", default="", help="If specified, a comma-separated list of properties to "
                                                         "be displayed. Otherwise, gets all properties.")
    @functools.wraps(func)
    def wrapper(properties="", exclude="", **kwargs):
        include = list(filter(lambda p: p != "", properties.split(",")))
        if len(include) == 0:
            include = ("",)
        exclude = list(filter(lambda p: p != "", exclude.split(",")))
        f = FieldsRequest(include, exclude)
        kwargs["fields"] = f
        return func(**kwargs)
    return wrapper


def get_manager_command(type_manager, sgqlc_type, name):
    def get_instance():
        conservator = Conservator.default()
        return type_manager(conservator)

    @click.group(name=name, help=f"View or manage {name}")
    def group():
        pass

    @group.command(name="fields", help=f"List the fields of a {sgqlc_type}")
    def fields_():
        click.echo(f"Field names of {sgqlc_type}:")
        for field in sgqlc_type.__field_names__:
            click.echo(field)

    @group.command(help=f"Print a {sgqlc_type} from an ID")
    @click.argument("id")
    @fields_request
    def get(fields, id):
        item = get_instance().from_id(id)
        item.populate(fields)
        click.echo(item)

    if issubclass(type_manager, SearchableTypeManager):
        @group.command(help=f"Search for {sgqlc_type}s")
        @click.argument('search_text')
        @fields_request
        def search(fields, search_text):
            items = get_instance().search(search_text).with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)

        @group.command(name="list", help=f"List all {sgqlc_type}s")
        @fields_request
        def list_(fields):
            items = get_instance().all().with_fields(fields)
            for number, item in enumerate(items):
                click.echo(item)

        @group.command(help=f"Count all {sgqlc_type}s, or the number of {sgqlc_type}s returned in a search")
        @click.argument('search_text', default="")
        def count(search_text):
            click.echo(get_instance().count(search_text))

    return group

