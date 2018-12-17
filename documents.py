import re
from typing import List, NamedTuple


class Document(NamedTuple):
    """Represents a document."""
    doc_id: int
    title: str
    summary: str
    keywords: List[str]

    @property
    def fields(self):
        return (field for field in self._fields if field != 'doc_id')


class ValueWithTokens(NamedTuple):
    raw: str
    tokens: List[str]


class DocumentWithTokens(Document):
    title: ValueWithTokens
    summary: ValueWithTokens
    keywords: ValueWithTokens

    @property
    def fields(self):
        return (getattr(self, field) for field in super().fields)


Collection = List[Document]
CollectionWithTokens = List[DocumentWithTokens]


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
        sections[section] = parse(section_content)
    return sections


def parse_document(doc: str) -> Document:
    doc_id = parse_id(doc)
    sections = parse_sections(doc)
    return Document(
        doc_id=doc_id,
        title=sections.get('T', ''),
        summary=sections.get('T', ''),
        keywords=sections.get('K', []),
    )


def parse_collection(raw_collection: List[str]) -> Collection:
    return [parse_document(doc) for doc in raw_collection]
