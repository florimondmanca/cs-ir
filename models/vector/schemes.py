"""Vector search weighting schemes."""

from collections import defaultdict
from typing import Dict, List, Union, Type
from math import sqrt, log10

from data_collections import Collection
from datatypes import DocID, PostingList, Term
from indexes import Index


class WeightingScheme:
    """Base weighting scheme class."""

    name: str

    def __init__(self, index: Index, query: List[str]):
        self.index = index
        self.query = query
        self.weights: List[Dict[DocID, float]] = [
            defaultdict(float) for _ in query
        ]

    def norm(self, doc_id: DocID) -> float:
        """Return a document's normalization factor.

        Parameters
        ----------
        doc_id : int

        Returns
        -------
        norm : float
        """
        raise NotImplementedError

    def tf(self, term: Term, doc: Union[DocID, str]) -> float:
        """Return the frequency of a term in a document.

        Parameters
        ----------
        term : str
        doc : str or int
            Either a string (for non-indexed documents) or a document ID
            (for indexed documents).

        Returns
        -------
        tf : float
        """
        raise NotImplementedError

    def df(self, term: Term) -> float:
        """Return the document frequency of a term.

        Parameters
        ----------
        term : str

        Returns
        -------
        df : float
        """
        raise NotImplementedError

    def __call__(self, term: Term, doc_id: DocID) -> float:
        """Compute the weight of a term relative to a document.

        Parameters
        ----------
        term : str
        doc_id : int

        Returns
        -------
        weight : float
        """
        return self.norm(doc_id) * self.df(term) * self.tf(term, doc_id)


class TfIdfSimple(WeightingScheme):
    """A simple tf-idf weighting scheme."""

    name = "simple"

    def norm(self, doc_id: DocID) -> float:
        return 1

    def tf(self, term: Term, doc: Union[DocID, str]) -> float:
        if isinstance(doc, str):
            # Reuse the tokenize algorithm.
            tokens = Collection().tokenize(doc)
            return sum(1 for token in tokens if token == term)

        doc_ids: PostingList = self.index.postings[term]
        return sum(1 for doc_id in doc_ids if doc_id == doc)

    def df(self, term: Term) -> float:
        return 1


class TfIdfComplex(TfIdfSimple):
    """A more complex tf-idf weighting scheme."""

    name = "complex"

    def norm(self, doc_id: DocID) -> float:
        d2 = sum(weights[doc_id] for weights in self.weights)
        return 1 / sqrt(d2) if d2 else 1

    def tf(self, term: Term, doc: Union[DocID, str]) -> float:
        tf = super().tf(term, doc)
        return 1 + log10(tf) if tf > 0 else 0

    def df(self, term: Term) -> float:
        df_t = self.index.df[term]
        return 1 / df_t if df_t else 0


SCHEMES: Dict[str, Type[WeightingScheme]] = {}

for _wcs in (TfIdfSimple, TfIdfComplex):
    SCHEMES[_wcs.name] = _wcs

