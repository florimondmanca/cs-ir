import os
import shutil
from itertools import count
from typing import Generator, List, Optional

from utils import find_files, grouped, multi_open

from .entry import Entry


def sort_external(entries: List[Entry], **kwargs) -> List[Entry]:
    with ExternalSorter(**kwargs) as sorter:
        for entry in entries:
            sorter.add(entry)
        return sorter.merge()


def _read_block(f) -> Generator[Entry, None, None]:
    for line in filter(None, map(str.strip, f)):
        yield Entry.from_line(line)


class ExternalSorter:
    """Helper to perform an external sort on index entries.

    Example
    -------

    ```python
    with ExternalSorter() as sorter:
        for entry in entries:
            sorter.add(entry)
        results = sorter.merge()
    ```
    """

    def __init__(self, block_size: int, temp_dir: str = "tmp"):
        self.block_size = block_size
        self._buffer: List[Entry] = []
        self.temp_path = temp_dir
        self._counter = None

    def __enter__(self):
        os.makedirs(self.temp_path, exist_ok=True)
        self._counter = count(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Cleaning up…")
        shutil.rmtree(self.temp_path, ignore_errors=True)

    def add(self, entry: Entry):
        """Push a new entry to the buffer.

        May trigger a flush to disk.

        Parameters
        ----------
        entry : Entry
        """
        if len(self._buffer) > self.block_size:
            self.flush()
        self._buffer.append(entry)

    def flush(self):
        """Flush the buffer to a new block file."""
        block_path = os.path.join(self.temp_path, str(next(self._counter)))

        entries = sorted(self._buffer)

        with open(block_path, "w") as f:
            f.writelines([entry.to_line() + "\n" for entry in entries])

        print(f"Flushed: {block_path}")

        self._buffer = []

    def _merge(self, out: str, *block_paths: str) -> None:
        print("merging", block_paths, "into", out)

        with multi_open(block_paths) as files, open(out, "w") as out_file:
            blocks = [_read_block(f) for f in files]

            # A list of pointers to the next entry to be merged from
            # each (sorted) block.
            # `None` means that the block has been merged completely.
            entry_pointers: List[Optional[Entry]] = [
                next(block, None) for block in blocks
            ]

            while any(entry_pointers):
                # Find entry of "smallest" entry in terms of token and docID.
                idx, smallest = min(
                    (i, entry)
                    for i, entry in enumerate(entry_pointers)
                    if entry is not None
                )

                # Write it to the output file.
                out_file.write(smallest.to_line())

                # Advance the entry pointer in the corresponding block.
                entry_pointers[idx] = next(blocks[idx], None)

        for block_path in block_paths:
            os.remove(block_path)

    def merge(self, batch_size: int = 100, _step: int = 0) -> List[Entry]:
        """Merge blocks into a single final list of entries.

        Blocks are batched in groups and merged recursively.

        Parameters
        ----------
        batch_size : int, optional
            The number of blocks in a merge batch. Defaults to 100.
        _step : int, optional
            Private parameter corresponding to the current processing stage.
        """
        block_paths = [path for _, path in find_files(self.temp_path)]

        if len(block_paths) == 1:
            # Only one block remaining => we're done.
            # Read the entries from it.
            last_block_path = block_paths[0]
            with open(last_block_path) as f:
                return list(_read_block(f))

        # Otherwise, batch blocks together and merge each of them into a
        # new block.
        for idx, batch in enumerate(grouped(batch_size, block_paths)):
            # The last `batch` may be end-padded with nones if the
            # number of items in `block_paths` is not a multiple of
            # `batch_size`.
            batch = filter(None, batch)

            out_path = os.path.join(self.temp_path, f"{_step}-{idx}")
            self._merge(out_path, *batch)

        # Merge the new blocks recursively.
        return self.merge(batch_size=batch_size, _step=_step + 1)
