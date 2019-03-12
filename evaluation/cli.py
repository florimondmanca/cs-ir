import os

import click
import matplotlib.pyplot as plt

from cli_utils import CollectionType
from data_collections import Collection
from indexes import build_index
from indexes import cli as indexes_cli
from models.boolean import Q
from models.boolean import cli as boolean_cli
from models.vector import cli as vector_cli
from models.vector import vector_search
from utils import Timer

from .evaluation import evaluate_requests, parse_answers, parse_requests


@click.group()
def cli():
    pass


def header(content: str):
    click.echo(click.style("\n" + content.center(40, "-") + "\n", fg="red"))


@cli.command()
@click.argument("collection", type=CollectionType())
def plot(collection: Collection):
    """Plot the precision-recall curve for a collection."""
    header("Vector search evaluation")

    queries = parse_requests(os.getenv("DATA_CACM_QUERIES"))
    target_results = parse_answers(os.getenv("DATA_CACM_QRELS"))
    index = build_index(collection)

    precisions = []
    recalls = []

    for k in range(1, 11):
        results = [set(vector_search(query, index, k)) for query in queries]
        precision, recall = evaluate_requests(results, target_results)
        precisions.append(precision)
        recalls.append(recall)

    plt.plot(precisions, recalls)
    plt.show()


@cli.command()
@click.argument("collection", type=CollectionType())
@click.option("-i", "--index", is_flag=True, default=False)
@click.pass_context
def showperfs(ctx: click.Context, collection: Collection, index: bool):
    click.echo(click.style(f"Collection: {collection.name}", fg="blue"))

    if index:
        header("Index build time")
        with Timer() as timer:
            ctx.invoke(
                indexes_cli.get_command(ctx, "build"),
                collection=collection,
                force=True,
            )
        click.echo(f"Index build time: {timer.total:.6f}s")

    header("Boolean request execution time")
    with Timer() as timer:
        ctx.invoke(
            boolean_cli,
            collection=collection,
            query=Q("algorithm") | Q("artifical"),
        )
    click.echo(f"{timer.total:.6f}s")

    header("Vector request execution time")
    with Timer() as timer:
        ctx.invoke(
            vector_cli, collection=collection, query="algorithm artificial"
        )
    click.echo(f"{timer.total:.6f}s")

    header("Index size")
    ctx.invoke(indexes_cli.get_command(ctx, "size"), collection=collection)


if __name__ == "__main__":
    cli()
