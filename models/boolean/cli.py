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
    """Request a collection using the boolean model.

    The query must be a valid Python expression comprised of terms wrapped
    in a `Q` object, and combined using the `|` (OR), `&` (AND) or `~` (NOT)
    operators.

    Examples:

        "Q('research')" => research
        "Q('algorithm') | Q('artificial')" => algorithm OR artificial
        "Q('France') & ~Q('Paris')" => France AND NOT Paris
    """
    index = build_index(collection)

    click.echo(f"Executing {query}...")
    results = query(index)

    click.echo(results)
