import re
from typing import List, Set

from documents import Document, DocumentWithTokens, ValueWithTokens
from resources import load_stop_words

_stop_words = load_stop_words()
non_alpha_numeric = re.compile('\W+')


def remove_stop_words(values: List[str], stop_words: Set[str] = None):
    if stop_words is None:
        stop_words = _stop_words
    for value in values:
        if value.lower() not in stop_words:
            yield value


def clean(values: List[str]) -> List[str]:
    return list(map(str.lower, remove_stop_words(values)))


def get_tokens(value: str) -> List[str]:
    """Tokenize words separated by non-alphanumeric characters."""
    return list(filter(None, non_alpha_numeric.split(value)))


def tokenize(document: Document) -> DocumentWithTokens:
    to_tokens = {
        'title': lambda v: clean(get_tokens(v)),
        'summary': lambda v: clean(get_tokens(v)),
        'keywords': lambda v: clean(v),
    }
    return DocumentWithTokens(
        doc_id=document.doc_id,
        **{
            field: ValueWithTokens(
                raw=getattr(document, field),
                tokens=to_tokens[field](getattr(document, field))
            )
            for field in to_tokens
        }
    )
