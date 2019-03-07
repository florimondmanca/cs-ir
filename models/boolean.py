"""Boolean request model implementation."""
from typing import List, Callable

import click

from cli_utils import CollectionType
from datatypes import PostingList, Term
from data_collections import Collection
from indexes import build_index, Index

Operation = Callable[[PostingList, Index], PostingList]


class Q:
    """Represents a boolean request, which can be combined with others."""

    def __init__(self, term: Term):
        self.term = term
        self.operations: List[Operation] = []

    def __and__(self, other: "Q") -> "Q":
        """Intersect with another request.

        Example
        -------
        >>> Q("a") & Q("b")
        """

        def intersect(left: PostingList, index: Index) -> PostingList:
            right = other(index)
            return sorted(set(left) & set(right))

        self.operations.append(intersect)

        return self

    def __or__(self, other: "Q") -> "Q":
        """Join with another request.

        Example
        -------
        >>> Q("a") | Q("b")
        """

        def union(left: PostingList, index: Index) -> PostingList:
            right = other(index)
            return sorted(set(left) | set(right))

        self.operations.append(union)
        return self

    def __invert__(self) -> "Q":
        """Negate the request.

        Example
        -------
        >>> ~Q("a")
        """

        def not_(left: PostingList, index: Index) -> PostingList:
            return sorted(index.doc_ids - set(left))

        self.operations.append(not_)
        return self

    def __call__(self, index: Index) -> PostingList:
        postings = index.postings[self.term]
        for operation in self.operations:
            postings = operation(postings, index)

        return postings

    def __str__(self) -> str:
        return f"<Q {self.operations}>"


@click.command()
@click.argument("collection", type=CollectionType())
def cli(collection: Collection):
    """Test the boolean model on a collection.

    The query is currently hardcoded: "algorithm | artifical".
    """
    index = build_index(collection)

    query = Q("algorithm") | Q("artifical")
    click.echo(f"Executing {query}...")
    results = query(index)

    click.echo(results)


if __name__ == "__main__":
    cli()
