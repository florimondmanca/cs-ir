import re
from typing import List, Set

with open('data/cacm.all', 'r') as data:
    lines = data.readlines()
    lines = [l.strip().replace('  ', ' ') for l in lines]
    content: str = ' '.join(lines)

with open('data/common_words.txt', 'r') as f:
    # Use a set for constant-time lookup
    stop_words = {l.strip() for l in f}

raw_docs = [doc for doc in content.split('.I ')[1:]]


def parse_id(doc: str) -> int:
    assert doc
    doc_id, *_ = doc.split()
    return int(doc_id)


def parse_sections(doc: str) -> dict:
    tokens = re.compile(r'\.(\w) ').split(doc)
    tokens.pop(0)
    sections = {}
    for section, section_content in zip(tokens[::2], tokens[1::2]):
        section_content = section_content.strip()
        parse = {
            'T': lambda s: s,
            'W': lambda s: s,
            'K': lambda s: s.split(', '),
        }.get(section)
        if parse is None:
            continue
        verbose = {
            'T': 'title',
            'W': 'summary',
            'K': 'keywords'
        }[section]
        sections[verbose] = parse(section_content)
    return sections


documents = []

for doc in raw_docs:
    doc_id = parse_id(doc)
    sections = parse_sections(doc)
    documents.append({'doc_id': doc_id, **sections})

print(len(documents))


def get_tokens(value: str) -> List[str]:
    """Tokenize words separated by non-alphanumeric characters."""
    return list(filter(None, re.split('\W+', value)))


def remove_stop_words(values):
    for value in values:
        if value not in stop_words:
            yield value


def clean(values: List[str]) -> List[str]:
    return [value.lower() for value in remove_stop_words(values)]


def tokenize(document: dict) -> dict:
    return {
        'doc_id': document['doc_id'],
        'title': {
            'raw': document['title'],
            'tokens': clean(get_tokens(document['title'])),
        },
        'summary': {
            'raw': document['summary'],
            'tokens': clean(get_tokens(document['summary'])),
        },
        'keywords': {
            'raw': document['keywords'],
            'tokens': clean(document['keywords']),
        },
    }
