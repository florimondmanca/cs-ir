import json
import os
import shutil
from collections import defaultdict
from contextlib import suppress
from itertools import count
from typing import DefaultDict, Dict, Generator, List, Optional, Set

from dotenv import load_dotenv

from collectshuns import CACM, Collection
from dataclasses import astuple, dataclass
from datatypes import DocID, PostingList, Term
from utils import find_files, multi_open

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BLOCK_SIZE = 10000


class Index:
    """Represents an index.

    Parameters
    ----------
    postings : dict
        Mapping of terms to a list of doc IDs.
    terms : set
        Set of unique tokens.
    doc_ids : set
        Set of unique doc IDs.
    df : dict
        Document frequency for each term, i.e. number of documents that
        contain the term.
    """

    def __init__(
        self,
        postings: Dict[Term, PostingList],
        terms: Set[Term],
        doc_ids: Set[DocID],
        df: Dict[Term, int],
        collection: Collection = None,
    ):
        self.postings: DefaultDict[Term, PostingList] = defaultdict(
            list, **postings
        )
        self.terms = terms
        self.doc_ids = doc_ids
        self.df = df
        self.collection = collection

    @property
    def num_documents(self) -> int:
        """Number of documents in the collection."""
        return len(self.doc_ids)

    @classmethod
    def from_cache(cls, collection: Collection):
        print(f"Loading {collection.name} index from cache…")
        with open(collection.index_cache, "r") as index_file:
            data = json.load(index_file)

        return Index(
            postings=data["postings"],
            terms=data["terms"],
            doc_ids=data["doc_ids"],
            df=data["df"],
            collection=collection,
        )

    @classmethod
    def build(
        cls, collection: Collection, block_size: int = DEFAULT_BLOCK_SIZE
    ):
        print("Building {collection.name} index…")
        with ExternalSorter(block_size) as sorter:
            for token, doc_id in collection:
                sorter.add(Entry(token, doc_id))
            result = sorter.merge()

        postings = defaultdict(list)
        doc_ids = set()
        terms = set()
        document_frequencies = defaultdict(int)
        for entry in result:
            # Note: if a token occurs multiple times in a document, the docID will
            # be present multiple times in the posting list.
            postings.setdefault(entry.token, [])
            postings[entry.token].append(entry.doc_id)
            doc_ids.add(entry.doc_id)
            terms.add(entry.token)
            document_frequencies[entry.token] += 1

        index = cls(
            postings=postings,
            terms=terms,
            doc_ids=doc_ids,
            df=document_frequencies,
            collection=collection,
        )

        index.to_cache()

        return index

    def to_cache(self):
        assert self.collection is not None
        data = {
            "collection": self.collection.name,
            "postings": self.postings,
            "terms": list(self.terms),
            "doc_ids": list(self.doc_ids),
            "df": self.df,
        }
        contents = json.dumps(data)
        with open(self.collection.index_cache, "w") as index_file:
            index_file.write(contents)


def build_index(
    collection: Collection, block_size: int = DEFAULT_BLOCK_SIZE
) -> Index:
    """Build an index out of a token stream.

    If the index has already been built and stored in the collection's index
    cache, it is used.

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
    collection : Collection
        Stream of token and doc_id pairs.
    block_size : int, optional
        Number of `(token, doc_id)` pairs per block. Defaults to 10,000.

    Returns
    -------
    index : dict
        A mapping of a `token` to a posting list (list of `doc_id`s).
    """
    with suppress(FileNotFoundError):
        return Index.from_cache(collection)

    return Index.build(collection, block_size=block_size)


# NOTE: `order=True` auto-generates comparison methods, allowing
# to sort a list of entries without specifying a `key` function.
# In this case, comparing two entries will be done by token and then by doc_id.
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

        block_paths = [path for _, path in find_files(self.temp_path)]
        with multi_open(block_paths) as files:
            blocks = [read_block(f) for f in files]

            # A list of the entry to be merged from each (sorted) block.
            # `None` means that the block has been merged completely.
            entries = [next(block, None) for block in blocks]

            while any(entries):
                # Find entry of smallest value
                idx, smallest = min(
                    (i, entry)
                    for i, entry in enumerate(entries)
                    if entry is not None
                )
                result.append(smallest)
                # Read next entry in block of smallest entry
                entries[idx] = next(blocks[idx], None)

        return result


if __name__ == "__main__":
    build_index(CACM(), 10000).to_cache()
