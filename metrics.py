from typing import List, Set, Counter as CounterType
from collections import Counter

from tokens import token_fields


def all_tokens(collection: List[dict]) -> List[str]:
    return [
        token
        for document in collection
        for field in token_fields(document)
        for token in document[field]['tokens']
    ]


def get_num_tokens(collection: List[dict]) -> int:
    return len(all_tokens(collection))


def get_vocabulary(collection: List[dict]) -> Set[str]:
    return set(all_tokens(collection))


def get_frequencies(collection: List[dict]) -> CounterType[str]:
    return Counter(all_tokens(collection))
