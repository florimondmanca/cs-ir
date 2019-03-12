import re
from typing import List

import click

from data_collections import Collection


def evaluate_relevancy(collection: Collection):
    click.echo("Evaluating vector search...")
    # TODO


QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")


def get_requests(path: str) -> List[str]:
    requests = []
    querying = False
    with open(path, "r") as f:
        lines = []
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
