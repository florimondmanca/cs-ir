import json
import os
from collections import defaultdict
from typing import DefaultDict, Dict, Set

from data_collections import Collection
from datatypes import DocID, PostingList, Term

from .entry import Entry
from .sort import sort_external

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
        print(f"Building index for {collection.name}…")
        entries = (Entry(token, doc_id) for token, doc_id in collection)
        result = sort_external(entries, block_size=block_size)

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
    collection: Collection,
    block_size: int = DEFAULT_BLOCK_SIZE,
    no_cache: bool = False,
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
    no_cache : bool, optional
        If `True`, skip using the cache (if it exists) and
        re-build the index from scratch.

    Returns
    -------
    index : dict
        A mapping of a `token` to a posting list (list of `doc_id`s).
    """
    if not no_cache:
        try:
            return Index.from_cache(collection)
        except FileNotFoundError as exc:
            print(f"Cache does not exist: {exc}")

    return Index.build(collection, block_size=block_size)
