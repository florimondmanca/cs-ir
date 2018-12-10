from typing import Set, List


def load_cacm() -> List[str]:
    with open('data/cacm.all', 'r') as data:
        lines = data.readlines()
        lines = [l.strip().replace('  ', ' ') for l in lines]
        content: str = ' '.join(lines)

    raw_docs = [doc for doc in content.split('.I ')[1:]]
    return raw_docs


def load_stop_words() -> Set[str]:

    with open('data/common_words.txt', 'r') as f:
        # Use a set for constant-time lookup
        return {l.strip() for l in f}
