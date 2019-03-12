import os

import click
from dotenv import load_dotenv

from cli_utils import CollectionType
from data_collections import Collection

from .index import build_index

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BLOCK_SIZE = 10000


@click.group()
def cli():
    pass


@cli.command()
@click.argument("collection", type=CollectionType())
@click.option("--block-size", "-b", default=DEFAULT_BLOCK_SIZE, type=int)
@click.option("--force", is_flag=True)
def build(collection: Collection, block_size: int, force: bool):
    if not force and collection.index_cache_exists:
        click.echo(
            click.style(
                f"{collection.name} index already exists! ", fg="yellow"
            ),
            nl=False,
        )
        click.echo(
            "Use "
            + click.style("--force", fg="red")
            + " to re-build it from scratch."
        )
        return

    build_index(collection, block_size=block_size, no_cache=True)
    click.echo(click.style("Done!", fg="green"))


@cli.command()
@click.argument("collection", type=CollectionType())
def size(collection):
    filesize = os.stat(collection.index_cache).st_size / 2 ** 20
    click.echo(f"{collection.index_cache} --- {filesize:.3f}MB")
