from typing import Dict, Type

import click

from .schemes import WeightingScheme


class WeightingSchemeClassType(click.ParamType):

    name = "wcs"

    def __init__(self, schemes: Dict[str, Type[WeightingScheme]]):
        super().__init__()
        self.schemes = schemes

    def convert(self, value, param, ctx) -> Type[WeightingScheme]:
        try:
            scheme = self.schemes[value]
        except KeyError:
            raise click.BadParameter(f"Unknown weighting scheme: {value}")
        else:
            return scheme
