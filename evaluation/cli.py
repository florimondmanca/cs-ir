import os

import click
import matplotlib.pyplot as plt

from cli_utils import CollectionType
from data_collections import Collection, CACM
from indexes import build_index
from indexes import cli as indexes_cli
from models.boolean import Q
from models.boolean import cli as boolean_cli
from models.vector import cli as vector_cli
from models.vector import vector_search
from utils import Timer

from .evaluation import precision_recall, parse_answers, parse_queries
from .measures import f_measure, e_measure


@click.group()
def cli():
    pass


def header(content: str):
    click.echo(click.style("\n" + content.center(40, "-") + "\n", fg="red"))


def get_queries() -> dict:
    return parse_queries(os.getenv("DATA_CACM_QUERIES"))


def get_answers() -> dict:
    return parse_answers(os.getenv("DATA_CACM_QRELS"))


@cli.command()
def plot():
    """Plot the precision-recall curve for the CACM collection."""
    header("Vector search precision-recall curve")

    collection = CACM()
    queries = get_queries()
    answers = get_answers()
    index = build_index(collection)

    click.echo("Computing precision and recall values…")

    precisions = []
    recalls = []

    for k in range(1, 31):
        found: dict = {
            query_id: set(vector_search(query, index, k=k))
            for query_id, query in queries.items()
        }
        precision, recall = precision_recall(found, answers)
        print("k:", k, "precision:", precision, "recall:", recall)
        precisions.append(precision)
        recalls.append(recall)

    plt.plot(precisions, recalls, label="precision")
    plt.plot(recalls, precisions, label="recall")
    plt.legend()
    plt.show()


@cli.command()
def rprec():
    """Compute the R-precision for queries on the CACM collection."""
    collection = CACM()
    header(f"R-precision for the {collection.name} collection")

    queries, answers = get_queries(), get_answers()
    index = build_index(collection)

    for query_id, query in queries.items():
        q_answers: set = answers.get(query_id, [])
        r = len(q_answers)
        results = vector_search(query, index, k=r)
        relevant = len(
            [result_id for result_id in results[:r] if result_id in q_answers]
        )
        prec = relevant / r if r else float("inf")
        click.echo(f"query {query_id}: {r}-precision = {prec}")


@cli.command()
def fe():
    """Show the F- and E-measure on the CACM collection."""
    collection = CACM()
    queries, answers = get_queries(), get_answers()
    index = build_index(collection)

    click.echo("Computing precision and recall…")
    found: dict = {
        query_id: set(vector_search(query, index, k=10))
        for query_id, query in queries.items()
    }
    precision, recall = precision_recall(found, answers)
    click.echo(f"Precision: {precision}")
    click.echo(f"Recall: {recall}")

    f = f_measure(precision, recall)
    e = e_measure(precision, recall)
    b = precision / recall

    click.echo(f"F-measure: {f:.2f}")
    click.echo(f"E-measure: {e:.2f}")
    click.echo(f"ß (= P/R): {b:.2f}")

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
