from collections import Counter

import click
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from cli_utils import CollectionType
from data_collections import Collection
from heaps import estimate, create_heaps

from evaluation import evaluate_performance

load_dotenv()


@click.command()
@click.argument("collection", type=CollectionType())
def cli(collection: Collection):
    """Inspect a collection and display key metrics.

    - Number of documents
    - Number of tokens
    - Vocabulary size
    - Heaps parameter estimation
    - Estimated size of the vocabulary for 10^6 tokens
    - 5 most frequent terms
    - Rank/frequency plots.
    """
    tokens, doc_ids = zip(*collection)

    doc_ids = set(doc_ids)

    click.echo(f"Documents: {len(doc_ids)}")

    # Q1
    num_tokens = len(tokens)
    click.echo(f"Tokens: {num_tokens}")

    # Q2
    vocabulary_size = len(set(tokens))
    click.echo(f"Terms (vocabulary size): {vocabulary_size}")

    # Q3
    half_tokens = tokens[::2]
    k, b = estimate(
        m1=vocabulary_size,
        t1=num_tokens,
        m2=len(set(half_tokens)),
        t2=len(half_tokens),
    )
    click.echo(f"Heaps parameters: k = {int(k)}, b = {round(b, 2)}")

    # Q4
    heaps = create_heaps(k, b)
    click.echo(
        f"Estimated vocabulary size for 1 million tokens: {int(heaps(1e6))}"
    )

    # Q5
    frequencies = Counter(tokens)
    t, f = zip(*sorted(frequencies.items(), key=lambda x: x[1], reverse=True))
    r = range(len(f))
    n = 5
    n_most_frequent_terms = ", ".join(
        f"{ti} ({fi})" for ti, fi in zip(t[:n], f[:n])
    )
    click.echo(f"{n} most frequent terms: {n_most_frequent_terms}")

    click.echo("Building and opening rank/frequency plots…")
    fig = plt.figure()
    fig.suptitle(
        f"Rank / Frequency plots. Collection: {collection.__class__.__name__}"
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

    # Evaluation
    evaluate_performance(collection)


if __name__ == "__main__":
    cli()
