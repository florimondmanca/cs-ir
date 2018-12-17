from math import log
from typing import Union, Tuple, Callable

Num = Union[int, float]


def estimate(m1: Num, t1: Num, m2: Num, t2: Num) -> Tuple[float, float]:
    b = t2 / t1 * log(m1 / m2)
    k = m1 / (t1 ** b)
    return k, b


def create_heaps(k: float, b: float) -> Callable[[float], float]:
    def get_vocab_size(t):
        return k * (t ** b)

    return get_vocab_size
