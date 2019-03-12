import re

import click

from cli_utils import CollectionType
from data_collections import Collection
from indexes import cli as indexes_cli
from models.boolean import Q, cli as boolean_cli
from models.vector import cli as vector_cli
from utils import Timer


@click.group()
def cli():
    pass


def header(content: str):
    click.echo(click.style("\n" + content.center(40, "-") + "\n", fg="red"))


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


def evaluate_relevancy(collection):
    click.echo("Evaluating vector search...")
    # TODO


QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")


def get_requests(file):
    requests = []
    querying = False
    with open(file, "r") as f:
        for line in f:
            if QUERY_REGEX.match(line):
                lines = []
                querying = True
            elif SECTION_REGEX.match(line) and querying:
                requests.append(" ".join(lines))
                querying = False
            elif querying:
                lines.append(line)
    return requests


if __name__ == "__main__":
    cli()
