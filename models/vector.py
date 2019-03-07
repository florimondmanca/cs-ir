"""Vector search model implementation."""
from collections import defaultdict
from heapq import nlargest
from math import sqrt, log10
from typing import List, Dict, Type, Union

import click

from cli_utils import CollectionType, WeightingSchemeClassType
from datatypes import DocID, Term, PostingList
from indexes import Index, build_index
from data_collections import Collection


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


@click.command()
@click.argument("collection", type=CollectionType())
@click.argument("query")
@click.option("--topk", "-k", type=int, default=10)
@click.option(
    "--weighting-scheme", "-w", "wcs", type=WeightingSchemeClassType(SCHEMES)
)
def cli(
    collection: Collection, query: str, topk: int, wcs: Type[WeightingScheme]
):
    """Test the boolean model on a collection."""
    index = build_index(collection)

    click.echo(f"Weighting scheme: {wcs.name}")

    click.echo("Query: ", nl=False)
    click.echo(click.style(query, fg="blue"))

    results = vector_search(query, index, k=topk, wcs=wcs)

    click.echo(click.style(f"Results: {results}", fg="green"))


if __name__ == "__main__":
    cli()
