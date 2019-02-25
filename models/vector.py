"""Vector search model implementation."""
from collections import defaultdict
from heapq import nlargest
from math import sqrt, log10
from typing import List, Dict, Type, Union

from datatypes import Index, DocID, Term, PostingList
from tokenizers import Tokenizer


class WeightingScheme:
    """Base weighting scheme class."""

    weights: List[Dict[DocID, float]]

    def __init__(self, index: Index, terms: List[str]):
        self.index = index
        self.terms = terms
        self.weights = [defaultdict(float) for _ in terms]

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


class TfIdf(WeightingScheme):
    """TF-IDF weighting scheme."""

    def norm(self, doc_id: DocID) -> float:
        d2 = sum(weights[doc_id] for weights in self.weights)
        return 1 / sqrt(d2)

    def tf(self, term: Term, doc: Union[DocID, str]) -> float:
        if isinstance(doc, str):
            # Reuse the tokenize algorithm.
            tokens = Tokenizer().tokenize(doc)
            return sum(1 for token in tokens if token == term)
        else:
            doc_ids: PostingList = self.index.postings[term]
            return sum(1 for doc_id in doc_ids if doc_id == doc)

    def df(self, term: Term) -> float:
        return log10(self.index.num_documents / self.index.df[term])


def vector_search(
    request: str, index: Index, k: int = 10, wcs: Type[WeightingScheme] = None
) -> List[DocID]:
    """Perform a vector-space search.

    Parameters
    ----------
    request : str
        A request as a string of words.
    index : Index
        A search index.
    k : int, optional
        Maximum number of documents to return. Defaults to 10.
    wcs : class, optional
        A weighting scheme class. Defaults to `TfIdf`.
    """
    if wcs is None:
        wcs = TfIdf

    scores: Dict[DocID, float] = {doc_id: 0 for doc_id in index.doc_ids}
    # Weights of request terms
    wq: List[float] = {}
    w = wcs(index=index, terms=request.split())

    for i, term in enumerate(w.terms):
        wq_i = w.tf(term, request) * w.df(term)
        wq.append(wq_i)

        for doc_id in index.postings[term]:
            w_i_dj = w(term, doc_id)
            w.weights[i][doc_id] = w_i_dj
            scores[doc_id] += w_i_dj * wq_i

    norm_q = sum(wq_i ** 2 for wq_i in wq)

    for doc_id in index.doc_ids:
        if scores[doc_id]:
            scores[doc_id] /= sqrt(w.norm(doc_id)) * sqrt(norm_q)

    top_k: list = nlargest(k, scores.items(), key=lambda item: item[1])
    return [doc_id for doc_id, _ in top_k]
