import os
import re
from itertools import count
from typing import List, Set

from datatypes import TokenStream, TokenDocIDStream
from resources import load_stop_words
from utils import find_files, find_dirs

HERE = os.path.dirname(os.path.abspath(__file__))


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

    location_env_var = "DATA_CACM_PATH"

    SECTIONS_OF_INTEREST = {"W", "T", "K"}
    DOC_ID_REGEX = re.compile(r'^\.(?P<section>I) (?P<doc_id>\d+)$')
    SECTION_REGEX = re.compile(r'^\.(?P<section>\w)$')

    def __init__(self):
        super().__init__()
        self.filename = os.getenv(self.location_env_var)

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


class Stanford(Tokenizer):
    location_env_var = "DATA_STANFORD_PATH"

    def __init__(self):
        super().__init__()
        self.dir_name = os.getenv(self.location_env_var)
        self.token_cache_filename = os.path.join(HERE, ".stanford_tokens.txt")
        self.doc_map_filename = os.path.join(HERE, ".stanford_doc_map.txt")

    def _from_dir(self) -> TokenDocIDStream:
        doc_ids = count(1)
        with open(self.doc_map_filename, "w") as doc_map, open(self.token_cache_filename, "w") as cache:
            for _, dir_path in find_dirs(self.dir_name):
                for filename, path in find_files(dir_path):
                    print(f"Loading {path}…")
                    doc_id = next(doc_ids)
                    doc_map.write(f"{doc_id} {filename}\n")
                    for token in self._from_file(path):
                        cache.write(f"{token} {doc_id}\n")
                        yield (token, doc_id)

    @staticmethod
    def _from_file(path: str):
        with open(path, "r") as f:
            for line in f:
                for token in line.split():
                    yield token

    def _from_cache(self) -> TokenDocIDStream:
        with open(self.token_cache_filename, "r") as f:
            print(f"Using cache at {self.token_cache_filename}…")
            for line in f:
                token, doc_id = line.split()
                yield token, int(doc_id)
            print("Finished consuming cache")

    def __iter__(self) -> TokenDocIDStream:
        try:
            yield from self._from_cache()
        except FileNotFoundError:
            yield from self._from_dir()
