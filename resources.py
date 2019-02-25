import os
from typing import Set


def load_stop_words() -> Set[str]:
    with open(os.getenv("DATA_STOP_WORDS_PATH"), "r") as f:
        # Use a set for constant-time lookup
        return {l.strip() for l in f}
