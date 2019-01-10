from collections import defaultdict
from typing import Iterator, Tuple, List, Dict, Set, DefaultDict

Token = str
Term = str
DocID = int
TokenStream = Iterator[Token]
TokenDocIDStream = Iterator[Tuple[Token, DocID]]
PostingList = List[DocID]


class Index:
    """Represents an index."""

    def __init__(
        self,
        postings: Dict[Term, PostingList],
        terms: Set[Term],
        doc_ids: Set[DocID],
    ):
        self.postings: DefaultDict[Term, PostingList] = defaultdict(
            int, **postings
        )
        self.terms = terms
        self.doc_ids = doc_ids
