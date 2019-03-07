import click

import data_collections


class CollectionType(click.ParamType):

    name = "collection"

    def convert(self, value, param, ctx):
        getattr(data_collections, "CACM")
        try:
            cls = getattr(data_collections, value)
        except AttributeError:
            raise click.BadParameter(
                f"Collection {value} not found in {data_collections}"
            )
        else:
            return cls()
