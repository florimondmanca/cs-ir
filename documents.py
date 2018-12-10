import re
from typing import List


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


def parse_document(doc: str) -> dict:
    doc_id = parse_id(doc)
    sections = parse_sections(doc)
    return {'doc_id': doc_id, **sections}


def parse_collection(collection: List[str]) -> List[dict]:
    return [parse_document(doc) for doc in collection]
