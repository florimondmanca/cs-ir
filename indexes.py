import json
import os
import shutil
from dataclasses import dataclass, astuple
from itertools import count
from typing import List, Optional, Generator

from dotenv import load_dotenv

import tokenizers
import utils

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))


def build_index(tokenizer: tokenizers.Tokenizer, block_size: int) -> dict:
    """Build an index out of a token stream.

    Notes
    -----
    This function uses the BSBI (Block Sort-Based Indexing) algorithm.
    - The stream is consumed and `(token, doc_id)` pairs are stored into
    a buffer.
    - When the buffer is full (as determined by `block_size`), it is sorted
    in memory and the result is stored on disk.
    - In the last step, intermediary files are read line-by-line to merge
    the results into the final index dictionary.

    Parameters
    ----------
    tokenizer : Tokenizer
        Stream of token and doc_id pairs.
    block_size : int
        Number of `(token, doc_id)` pairs per block.

    Returns
    -------
    index : dict
        A mapping of a `token` to a posting list (list of `doc_id`s).
    """
    with ExternalSorter(block_size) as sorter:
        for token, doc_id in tokenizer:
            sorter.add(Entry(token, doc_id))
        result = sorter.merge()

    # Build the index by grouping the results by token
    index = {}
    for entry in result:
        index.setdefault(entry.token, [])
        index[entry.token].append(entry.doc_id)
    return index


# NOTE: `order=True` auto-generates comparison methods, allowing
# to sort a list of entries without specifying a `key` function.
@dataclass(order=True)
class Entry:
    """Entry in a collection made of a token ID and document ID."""

    token: str
    doc_id: int

    def to_line(self, nl=True) -> str:
        return " ".join(map(str, astuple(self))) + (nl and "\n" or "")

    @classmethod
    def from_line(cls, line: str) -> Optional["Entry"]:
        token, doc_id = line.split()
        return cls(token, int(doc_id))


def read_block(f) -> Generator[Entry, None, None]:
    for line in filter(None, map(str.strip, f)):
        yield Entry.from_line(line)


class ExternalSorter:
    """Helper to perform an external sort.

    Entries are pushed with the `.add()` method, which may flush a new block
    to disk when the buffer is full.
    The `.sort()` method returns the merged dictionary.

    This must be used as a context manager that will initialize a folder
    for intermediary results in enter, and clean it up on exit.
    """

    def __init__(self, block_size: int, temp_dir: str = "tmp"):
        self.block_size = block_size
        self._buffer: List[Entry] = []
        self.temp_path = temp_dir
        self._counter = None

    def __enter__(self):
        os.makedirs(self.temp_path, exist_ok=True)
        self._counter = count(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_path, ignore_errors=True)

    def add(self, entry: Entry):
        """Push a new entry to the buffer.

        May trigger a flush to disk.

        Parameters
        ----------
        entry : Entry
        """
        if len(self._buffer) > self.block_size:
            self.flush()
        self._buffer.append(entry)

    def flush(self):
        """Flush the buffer to a new block file."""
        block_path = os.path.join(self.temp_path, str(next(self._counter)))

        entries = sorted(self._buffer)

        with open(block_path, "w") as f:
            f.writelines([entry.to_line() + "\n" for entry in entries])

        self._buffer = []

    def merge(self) -> List[Entry]:
        """Merge blocks into a single final dictionary."""
        result: List[Entry] = []

        block_paths = [path for _, path in utils.find_files(self.temp_path)]
        with utils.multi_open(block_paths) as files:
            blocks = [read_block(f) for f in files]

            # A list of the entry to be merged from each (sorted) block.
            # `None` means that the block has been merged completely.
            entries = [next(block, None) for block in blocks]

            while any(entries):
                # Find entry of smallest value
                idx, smallest = min(
                    (i, entry) for i, entry in enumerate(entries)
                    if entry is not None
                )
                result.append(smallest)
                # Read next entry in block of smallest entry
                entries[idx] = next(blocks[idx], None)

        return result


if __name__ == '__main__':
    index = build_index(tokenizers.CACM(), 10000)
    with open("results/index.json", "w") as index_file:
        index_file.write(json.dumps(index))
