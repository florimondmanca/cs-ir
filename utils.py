import os
from typing import Tuple, Generator


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
