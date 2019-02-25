from collections import Counter

import click
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from cli_utils import validate_tokenizer
from tokenizers import Tokenizer
from heaps import estimate, create_heaps

load_dotenv()


def inspect(tokenizer: Tokenizer):
    tokens, doc_ids = zip(*tokenizer)

    doc_ids = set(doc_ids)

    print("Documents:", len(doc_ids))

    # Q1
    num_tokens = len(tokens)
    print("Tokens:", num_tokens)

    # Q2
    vocabulary_size = len(set(tokens))
    print("Terms (vocabulary size):", vocabulary_size)

    # Q3
    half_tokens = tokens[::2]
    k, b = estimate(
        m1=vocabulary_size,
        t1=num_tokens,
        m2=len(set(half_tokens)),
        t2=len(half_tokens),
    )
    print("Heaps parameters:", "k =", int(k), "b =", round(b, 2))

    # Q4
    heaps = create_heaps(k, b)
    print("Estimated vocabulary size for 1 million tokens:", int(heaps(1e6)))

    # Q5
    frequencies = Counter(tokens)
    t, f = zip(*sorted(frequencies.items(), key=lambda x: x[1], reverse=True))
    r = range(len(f))
    n_most = 5
    print(
        n_most,
        "most frequent terms:",
        ", ".join(f"{ti} ({fi})" for ti, fi in zip(t[:n_most], f[:n_most])),
    )

    fig = plt.figure()
    fig.suptitle(
        f"Rank / Frequency plots. Collection: {tokenizer.__class__.__name__}"
    )

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_xlabel("$r$")
    ax1.set_ylabel("$f$")
    ax1.plot(r, f)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_xlabel("$\log(r)$")
    ax2.set_ylabel("$\log(f)$")
    ax2.loglog(r, f)

    plt.show()


@click.command()
@click.argument("tokenizer", callback=validate_tokenizer)
def cli(tokenizer: Tokenizer):
    """Inspect a collection with language processing algorithms.
    
    - Number of documents
    - Number of tokens
    - Vocabulary size
    - Heaps parameter estimation
    - Estimated size of the vocabulary for 10^6 tokens
    - 5 most frequent terms
    - Rank/frequency plots.
    """
    inspect(tokenizer)


if __name__ == "__main__":
    cli()
