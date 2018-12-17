from typing import List, Set, Counter as CounterType
from collections import Counter

from documents import CollectionWithTokens


def all_tokens(collection: CollectionWithTokens) -> List[str]:
    return [
        token
        for document in collection
        for field in document.fields
        for token in field.tokens
    ]


def get_num_tokens(collection: CollectionWithTokens) -> int:
    return len(all_tokens(collection))


def get_vocabulary(collection: CollectionWithTokens) -> Set[str]:
    return set(all_tokens(collection))


def get_frequencies(collection: CollectionWithTokens) -> CounterType[str]:
    return Counter(all_tokens(collection))
