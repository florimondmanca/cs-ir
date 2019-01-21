from collections import defaultdict
from typing import Iterator, Tuple, List, Dict, Set, DefaultDict

Token = str
Term = str
DocID = int
TokenStream = Iterator[Token]
TokenDocIDStream = Iterator[Tuple[Token, DocID]]
PostingList = List[DocID]


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
    ):
        self.postings: DefaultDict[Term, PostingList] = defaultdict(
            int, **postings
        )
        self.terms = terms
        self.doc_ids = doc_ids
        self.df = df

    @property
    def num_documents(self) -> int:
        """Number of documents in the collection."""
        return len(self.doc_ids)
