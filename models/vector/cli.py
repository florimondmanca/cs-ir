from typing import Type

import click

from cli_utils import CollectionType
from data_collections import Collection
from indexes import build_index

from .cli_utils import WeightingSchemeClassType
from .schemes import SCHEMES, WeightingScheme, TfIdfSimple
from .search import vector_search


@click.command()
@click.argument("collection", type=CollectionType())
@click.argument("query")
@click.option("--topk", "-k", type=int, default=10, show_default=True)
@click.option(
    "--weighting-scheme",
    "-w",
    "wcs",
    type=WeightingSchemeClassType(SCHEMES),
    default=TfIdfSimple.name,
    show_default=True,
)
def cli(
    collection: Collection, query: str, topk: int, wcs: Type[WeightingScheme]
):
    """Search a collection using the vector model."""
    index = build_index(collection)

    click.echo(f"Weighting scheme: {wcs.name}")

    click.echo("Query: ", nl=False)
    click.echo(click.style(query, fg="blue"))

    results = vector_search(query, index, k=topk, wcs=wcs)

    click.echo(click.style(f"Results: {results}", fg="green"))
