import re
from typing import List

QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")


def parse_requests(path: str) -> List[str]:
    requests = []
    querying = False

    with open(path, "r") as f:
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


def parse_answers(path: str) -> List[str]:
    answers = []

    with open(path, "r") as f:
        for line in f:
            query_id, answer_id, *_ = line.strip().split(" ")
            query_id = int(query_id)
            answer_id = int(answer_id)
            same_query = query_id == len(answers)
            if same_query:
                answers[-1].add(answer_id)
            else:
                answers.append({answer_id})

    return answers


def evaluate_requests(found_ids: List[set], target_ids: List[set]):
    precision = sum(
        [len(fids & tids) for fids, tids in zip(found_ids, target_ids)]
    ) / sum([len(fids) for fids in found_ids])
    rappel = sum(
        [len(fids & tids) for fids, tids in zip(found_ids, target_ids)]
    ) / sum([len(tids) for tids in target_ids])
    return precision, rappel
