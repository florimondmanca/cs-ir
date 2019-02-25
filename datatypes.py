from typing import Iterator, Tuple, List

Token = str
Term = str
DocID = int
TokenStream = Iterator[Token]
TokenDocIDStream = Iterator[Tuple[Token, DocID]]
PostingList = List[DocID]
