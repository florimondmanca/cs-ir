from typing import Set


def load_stop_words() -> Set[str]:
    with open('data/common_words.txt', 'r') as f:
        # Use a set for constant-time lookup
        return {l.strip() for l in f}
