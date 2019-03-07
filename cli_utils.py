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


class WeightingSchemeClassType(click.ParamType):

    name = "wcs"

    def __init__(self, schemes):
        super().__init__()
        self.schemes = schemes

    def convert(self, value, param, ctx):
        try:
            scheme = self.schemes[value]
        except KeyError:
            raise click.BadParameter(f"Unknown weighting scheme: {value}")
        else:
            return scheme
