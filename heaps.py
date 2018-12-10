from math import log


def estimate(m1, t1, m2, t2):
    b = t2 / t1 * log(m1 / m2)
    k = m1 / (t1 ** b)
    return k, b


def create_heaps(k, b):
    def get_vocab_size(t):
        return k * (t ** b)

    return get_vocab_size
