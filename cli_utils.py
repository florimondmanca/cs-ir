import click

import collectshuns


class CollectionType(click.ParamType):

    name = "collection"

    def convert(self, value, param, ctx):
        getattr(collectshuns, "CACM")
        try:
            cls = getattr(collectshuns, value)
        except AttributeError:
            raise click.BadParameter(
                f"Collection {value} not found in {collectshuns}"
            )
        else:
            return cls()
