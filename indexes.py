import os
import shutil
from contextlib import ExitStack
from itertools import count

import tokenizers
import utils

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))


def build_index(tokenizer: tokenizers.Tokenizer, buffer_size: int):
    buffer = []
    cache = Cache()

    for token_id, doc_id in tokenizer:
        if len(buffer) < buffer_size:
            buffer.append((token_id, doc_id))
        else:
            cache.write(sorted(buffer, key=lambda v: (v[0], int(v[1]))))
            buffer = []

    cache.merge()
    cache.clean()


class ItemWrapper:

    def __init__(self, f):
        self.f = f

    def read(self):
        value = self.f.readline()
        if value:
            return value.split()
        else:
            return None


class Cache:

    def __init__(self):
        self.dir_name = 'bsbi-cache'
        os.makedirs(os.path.join(HERE, self.dir_name), exist_ok=True)
        self.counter = count(1)

    def write(self, buffer):
        with open(os.path.join(HERE, self.dir_name, str(next(self.counter))), 'w') as f:
            f.writelines([" ".join(item) + "\n" for item in buffer])

    def merge(self):
        file_names = utils.find_files(os.path.join(HERE, self.dir_name))
        with ExitStack() as stack:
            files = [ItemWrapper(stack.enter_context(open(file_path))) for _, file_path in file_names]
            with open("output", "w") as out:
                values = [f.read() for f in files]
                while any(values):
                    index, min_value = min(filter(lambda v: v[1] is not None, enumerate(values)),
                                           key=lambda v: (v[1][0], int(v[1][1])))
                    values[index] = files[index].read()
                    out.write(" ".join(min_value) + "\n")

    def clean(self):
        shutil.rmtree(os.path.join(HERE, self.dir_name))


build_index(tokenizers.CACM(), 10000)
