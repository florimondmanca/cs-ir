import re
from typing import List

import click

from data_collections import Collection


def evaluate_relevancy(collection):
    click.echo("Evaluating vector search...")
    queries = parse_requests(os.getenv("DATA_CACM_QUERIES"))
    target_results = parse_answers(os.getenv("DATA_CACM_QRELS"))
    index = build_index(collection)
    precisions = []
    rappels = []

    for k in range(1,10):
        results = [set(vector_search(query, index, k)) for query in queries]
        precision, rappel = evaluate_requests(results, target_results)
        precisions.append(precision)
        rappels.append(rappel)

    plt.plot(precisions, rappels)
    plt.show()


QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")


def parse_requests(file):
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
                lines.append(line.strip())
    return requests

def parse_answers(file):
    answers = []
    with open(file, 'r') as f:
        for line in f:
            if int(line.split(" ")[0]) == len(answers):
                answers[-1].add(int(line.split(" ")[1]))
            else:
                answers.append({int(line.split(" ")[1])})
    return answers

def evaluate_requests(found_ids: List[set], target_ids: List[set]):
    precision = sum([len(fids & tids) for fids, tids in zip(found_ids, target_ids)]) / sum([len(fids) for fids in found_ids])
    rappel = sum([len(fids & tids) for fids, tids in zip(found_ids, target_ids)]) / sum([len(tids) for tids in target_ids])
    return precision, rappel    
