import os
from contextlib import ExitStack, contextmanager
from typing import Tuple, Generator, List, Iterable, Any
from itertools import zip_longest


def find_files(root: str) -> Generator[Tuple[str, str], None, None]:
    return (
        (e.name, os.path.join(root, e.name))
        for e in os.scandir(root)
        if e.is_file()
    )


def find_dirs(root: str) -> Generator[Tuple[str, str], None, None]:
    return (
        (e.name, os.path.join(root, e.name))
        for e in os.scandir(root)
        if e.is_dir()
    )


@contextmanager
def multi_open(paths: List[str]):
    """Open multiple files."""
    # NOTE: ExitStack calls `__exit__()` on the registered context managers.
    # We use it to make sure all opened files are closed when
    # exiting this context.
    with ExitStack() as stack:
        yield [stack.enter_context(open(path)) for path in paths]


def grouped(n: int, iterable: Iterable, fillvalue: Any = None):
    """Group items of an iterable in groups of a most n elements.

    Example
    -------
    grouped(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    """
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
