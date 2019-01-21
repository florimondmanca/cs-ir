"""Boolean request model implementation."""
from typing import List, Callable

import pytest

from datatypes import Index, PostingList, Term

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


# NOTE: run these tests with `pytest <this_file>`

@pytest.fixture
def index():
    return Index(
        postings={"a": [0, 1, 3], "b": [0, 2]},
        doc_ids={0, 1, 2, 3},
        terms={"a", "b"},
    )


def test_single_term(index):
    assert (Q("a"))(index) == [0, 1, 3]


def test_and(index):
    assert (Q("a") & Q("b"))(index) == [0]


def test_or(index):
    assert (Q("a") | Q("b"))(index) == [0, 1, 2, 3]


def test_not(index):
    assert (~Q("a"))(index) == [2]
    assert (~(~Q("a")))(index) == [0, 1, 3]


def test_complex_queries(index):
    assert (Q("a") & ~Q("b"))(index) == [1, 3]
    assert ((Q("a") | Q("b")) & ~Q("a"))(index) == [2]
    assert (Q("b") | (Q("b") & Q("a")))(index) == [0, 2]
