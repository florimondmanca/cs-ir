"""Vector search algorithm implementation."""
from heapq import nlargest
from typing import Dict, List, Type
from math import sqrt

from data_collections import Collection
from datatypes import DocID
from indexes import Index

from .schemes import WeightingScheme, TfIdfSimple


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
        A weighting scheme class. Defaults to `TfIdfSimple`.
    """
    if wcs is None:
        wcs = TfIdfSimple

    scores: Dict[DocID, float] = {doc_id: 0 for doc_id in index.doc_ids}
    # Weights of request terms
    wq: List[float] = []
    w = wcs(index=index, query=list(Collection().tokenize(request)))

    for term_id, term in enumerate(w.query):
        w_i_q = w.weights[term_id][request] = w.tf(term, request) * w.df(term)
        wq.append(w_i_q)

        for doc_id in index.postings[term]:
            w_i_dj = w(term, doc_id)
            w.weights[term_id][doc_id] = w_i_dj
            scores[doc_id] += w_i_dj * w_i_q

    norm_q = sum(w_i_q ** 2 for w_i_q in wq)

    for doc_id in index.doc_ids:
        if scores[doc_id]:
            scores[doc_id] /= sqrt(w.norm(doc_id)) * sqrt(norm_q) or 1

    top_k: list = nlargest(k, scores.items(), key=lambda item: item[1])
    return [doc_id for doc_id, _ in top_k]
