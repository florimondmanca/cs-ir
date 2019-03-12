from time import time
from indexes import build_index
import click
from models.boolean.search import Q
from models.vector.search import vector_search
import os
import re

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

    t0 = time()
    query = "algorithm artificial"
    click.echo(f"Executing query \"{query}\"...")
    results = vector_search(query, index)
    t1 = time()

    click.echo(results)
    click.echo("Results found in {time:.6f}s".format(time=(t1-t0)))

    # Disk space
    for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")):
        click.echo("{file} ---- {file_size:.3f}MB".format(file=file, file_size=(os.stat(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", file)).st_size >> 20)))
        click.echo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", file))
    

def evaluate_relevancy(collection):
    click.echo("Evaluating vector search...")

def get_requests(file):
    QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
    SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")
    requests = []
    querying = False
    with open(file, 'r') as f:
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
    