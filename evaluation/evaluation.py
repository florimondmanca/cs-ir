import re
from typing import Dict, Tuple

ID_REGEX = re.compile(r"^\.(?P<section>I) (?P<id>\d+)$")
QUERY_REGEX = re.compile(r"^\.(?P<section>W)$")
SECTION_REGEX = re.compile(r"^\.(?P<section>\w)$")


def parse_queries(path: str) -> Dict[int, str]:
    queries = {}

    querying = False
    query_id = None
    lines = []

    with open(path, "r") as f:
        for line in f:
            m = ID_REGEX.match(line)
            if m:
                query_id = int(m.group("id"))
                continue

            if QUERY_REGEX.match(line):
                lines = []
                querying = True
            elif SECTION_REGEX.match(line) and querying:
                assert query_id is not None
                queries[query_id] = " ".join(lines)
                querying = False
            elif querying:
                lines.append(line.strip())

    return queries


def parse_answers(path: str) -> Dict[int, set]:
    answers = {}

    with open(path, "r") as f:
        for line in f:
            query_id, answer_id, *_ = line.strip().split(" ")
            query_id = int(query_id)
            answer_id = int(answer_id)
            answers.setdefault(query_id, set())
            answers[query_id].add(answer_id)

    return answers


def precision_recall(
    found: Dict[int, set], answers: Dict[int, set]
) -> Tuple[float, float]:

    found = list(found.values())
    answers = list(answers.values())

    def count(sets):
        return sum(len(s) for s in sets)

    found_answers = [f & a for f, a in zip(found, answers)]

    precision = count(found_answers) / count(found)
    recall = count(found_answers) / count(answers)

    return precision, recall
