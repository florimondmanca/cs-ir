import re
from typing import List, Set, Generator

from resources import load_stop_words

_stop_words = load_stop_words()
non_alpha_numeric = re.compile('\W+')


def get_tokens(value: str) -> List[str]:
    """Tokenize words separated by non-alphanumeric characters."""
    return list(filter(None, non_alpha_numeric.split(value)))


def remove_stop_words(values: List[str], stop_words: Set[str] = None):
    if stop_words is None:
        stop_words = _stop_words
    for value in values:
        if value.lower() not in stop_words:
            yield value


def clean(values: List[str]) -> List[str]:
    return list(map(str.lower, remove_stop_words(values)))


def token_fields(document: dict) -> Generator[str, None, None]:
    return (field for field in document if field != 'doc_id')


def tokenize(document: dict) -> dict:
    tokenizers = {
        'title': lambda v: clean(get_tokens(v)),
        'summary': lambda v: clean(get_tokens(v)),
        'keywords': lambda v: clean(v),
    }
    return {
        'doc_id': document['doc_id'],
        **{
            field: {
                'raw': document[field],
                'tokens': tokenizers[field](document[field])
            }
            for field in token_fields(document)
        }
    }
