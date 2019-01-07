import re
from typing import Tuple, List, Set, Iterator

from resources import load_stop_words

Token = str
DocID = str
TokenStream = Iterator[Token]
TokenDocIDStream = Iterator[Tuple[Token, DocID]]


class Tokenizer:
    """Base tokenizer interface.

    A tokenizer is an iterator (in Python sense) that yields a stream
    of (token, doc_id) pairs.
    """

    NON_ALPHA_NUMERIC = re.compile('\W+')

    def __init__(self):
        self.stop_words = load_stop_words()

    def tokenize(self, text: str, stop_words: Set[str] = None) -> TokenStream:
        """Separate a text into a set of tokens."""
        if stop_words is None:
            stop_words = self.stop_words
        tokens = filter(None, self.NON_ALPHA_NUMERIC.split(text))
        tokens = map(str.lower, tokens)
        tokens = filter(lambda t: t not in stop_words, tokens)
        return tokens

    def __iter__(self) -> TokenDocIDStream:
        raise NotImplementedError


class CACM(Tokenizer):
    """Tokenizer for the CACM collection."""

    SECTIONS_OF_INTEREST = {"W", "T", "K"}
    DOC_ID_REGEX = re.compile(r'^\.(?P<section>I) (?P<doc_id>\d+)$')
    SECTION_REGEX = re.compile(r'^\.(?P<section>\w)$')

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def _from_file(self) -> TokenDocIDStream:
        """Load tokens and doc_ids from the CACM collection from disk."""
        # The doc ID and section currently being parsed
        doc_id = None
        current_section = None
        # Store the lines of text for the current section
        buffer: List[str] = []

        def flush() -> TokenDocIDStream:
            """Generate tokens and doc_ids from the buffer, and reset it."""
            nonlocal buffer
            text = " ".join(buffer)
            assert doc_id is not None, "doc_id unexpectedly None"
            for token in self.tokenize(text):
                yield (token, doc_id)
            buffer = []

        with open(self.filename, "r") as f:
            for line in f:
                # Is this line a doc_id line?
                match = self.DOC_ID_REGEX.match(line)
                if match is not None:
                    if doc_id is not None:
                        # Although most examples show that the last section
                        # before a new  "I" is "X", in which we're not
                        # interested, it is possible that the before is not
                        # empty.
                        yield from flush()
                    doc_id = match.group("doc_id")
                    current_section = match.group("section")
                    continue

                # If not, is this a section line?
                match = self.SECTION_REGEX.match(line)
                if match is not None:
                    # Flush the buffer for the previous section
                    yield from flush()
                    current_section = match.group("section")

                # This line is a simple text line. Add it to the buffer, but
                # only if we're interested in this section.
                elif current_section in self.SECTIONS_OF_INTEREST:
                    # strip() to remove white spaces, tabs and newlines.
                    buffer.append(line.strip())

    def __iter__(self) -> TokenDocIDStream:
        yield from self._from_file()
