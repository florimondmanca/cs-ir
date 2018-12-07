import re

with open('data/cacm.all', 'r') as data:
    content: str = data.read()

raw_docs = [doc.replace('\n', ' ') for doc in content.split('.I ')[1:]]


def parse_id(doc: str) -> str:
    assert doc, 'No doc: ' + doc
    doc_id, *_ = doc.split()
    return doc_id


def parse_sections(doc: str) -> dict:
    tokens = re.compile(r'\.(\w) ').split(doc)
    tokens.pop(0)
    sections = {}
    for section, section_content in zip(tokens[::2], tokens[1::2]):
        # TODO parse section content
        # TODO store by field name instead of raw section ID (W, T, K)
        sections[section] = section_content
    return sections


documents = []

for doc in raw_docs:
    doc_id = parse_id(doc)
    sections = parse_sections(doc)
    documents.append({'doc_id': doc_id, **sections})

print(len(documents))
