from dataclasses import astuple, dataclass
from typing import Optional


# NOTE: `order=True` auto-generates comparison methods, allowing
# to sort a list of entries without specifying a `key` function.
# In this case, comparing two entries will be done by token and then by doc_id.
@dataclass(order=True)
class Entry:
    """Entry in a collection made of a token ID and document ID."""

    token: str
    doc_id: int

    def to_line(self, nl=True) -> str:
        return " ".join(map(str, astuple(self))) + (nl and "\n" or "")

    @classmethod
    def from_line(cls, line: str) -> Optional["Entry"]:
        token, doc_id = line.split()
        return cls(token, int(doc_id))
