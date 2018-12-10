from random import shuffle

import matplotlib.pyplot as plt

from documents import parse_collection
from heaps import estimate, create_heaps
from metrics import get_num_tokens, get_vocabulary, get_frequencies
from resources import load_cacm
from tokens import tokenize

collection = parse_collection(load_cacm())
collection = list(map(tokenize, collection))

print('Documents:', len(collection))

# Q1
num_tokens = get_num_tokens(collection)
print('Tokens:', num_tokens)

# Q2
vocabulary_size = len(get_vocabulary(collection))
print('Terms (vocabulary size):', vocabulary_size)

# Q3
# NOTE: how the collection is cut in 2 affects the value of k and b.
# We compute an average value by shuffling the collection multiple times.
ks, bs = [], []
for _ in range(10):
    shuffle(collection)
    half_collection = collection[::2]
    assert len(half_collection) == len(collection) // 2
    k, b = estimate(
        m1=vocabulary_size,
        t1=num_tokens,
        m2=len(get_vocabulary(half_collection)),
        t2=get_num_tokens(half_collection),
    )
    ks.append(k)
    bs.append(b)
k = sum(ks) / len(ks)
b = sum(bs) / len(bs)
print('Heaps parameters:', 'k =', int(k), 'b =', round(b, 2))

# Q4
heaps = create_heaps(k, b)
print('Vocabulary size for 1 million tokens:', int(heaps(1e6)))

# Q5
frequencies = get_frequencies(collection)
freq_desc = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
r, f = zip(*freq_desc)
n_most = 5
print(
    n_most, 'most frequent:',
    ', '.join(f'{ri} ({fi})' for ri, fi in zip(r[:n_most], f[:n_most]))
)

plt.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
# plt.plot(r, f)
# plt.show()
