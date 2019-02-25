import pytest

from indexes import Index
from models.boolean import Q


@pytest.fixture(name="index")
def fixture_index():
    return Index(
        postings={"a": [0, 1, 3], "b": [0, 2]},
        doc_ids={0, 1, 2, 3},
        terms={"a", "b"},
        df={"a": 3, "b": 2},
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
