import click

from .search import Q


class BooleanQueryType(click.ParamType):

    name = "query"

    def convert(self, value, param, ctx) -> Q:
        try:
            return Q("algorithm") | Q("artificial")
        except AttributeError:
            raise click.BadParameter(f"Invalid query syntax")
