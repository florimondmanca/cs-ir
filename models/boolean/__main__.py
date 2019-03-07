import click

from cli_utils import CollectionType
from data_collections import Collection
from indexes import build_index

from .cli_utils import BooleanQueryType
from .search import Q


@click.command()
@click.argument("collection", type=CollectionType())
@click.argument("query", type=BooleanQueryType())
def cli(collection: Collection, query: Q):
    """Test the boolean model on a collection.

    The query is currently hardcoded: "algorithm | artifical".
    """
    index = build_index(collection)

    click.echo(f"Executing {query}...")
    results = query(index)

    click.echo(results)


if __name__ == "__main__":
    cli()
