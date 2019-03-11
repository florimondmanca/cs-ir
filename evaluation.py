from time import time
from indexes import build_index
import click
from models.boolean import Q
from models.vector import vector_search
import os

def evaluate_performance(collection):
    # Index build time
    t0 = time()
    index = build_index(collection, no_cache=True)
    t1 = time()
    click.echo("Index build time: {time:.6f}s".format(time=(t1-t0)))

    # Query response time
    t0 = time()
    query = Q("algorithm") | Q("artifical")
    click.echo(f"Executing {query}...")
    results = query(index)
    t1 = time()

    click.echo(results)
    click.echo("Results found in {time:.6f}s".format(time=(t1-t0)))

    """t0 = time()
    query = "algorithm artificial"
    click.echo(f"Executing query \"{query}\"...")
    results = vector_search(query, index)
    t1 = time()

    click.echo(results)
    click.echo("Results found in {time:.6f}s".format(time=(t1-t0)))"""

    # Disk space
    for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")):
        click.echo("{file} ---- {file_size}MB".format(file=file, file_size=(os.stat(os.path.abspath(file)).st_size >> 20)))
    

