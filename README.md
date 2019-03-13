# CS-IR

This repository is home to the code for an _Information Retrieval_ (IR) course project.

## Goal

The project aims at implementing various notions of IR such as tokenization, indexing and evaluation, and applying them to real-world text datasets in order to build a rudimentary yet performant search engine.

## Installation

- Place the CACM and CS276 datasets on your computer, then create a `.env` file with the following variables:

```dotenv
DATA_STOP_WORDS_PATH=path/to/common_words.txt
DATA_CACM_PATH=path/to/cacm.all
DATA_CACM_QUERIES=path/to/query.text
DATA_CACM_QRELS=path/to/qrels.text
DATA_CS276_PATH=/path/to/pa1-data
```

- Get [Python] 3.7+ and [Pipenv] (`pip install pipenv`) and install dependencies:

```bash
pipenv install
```

- Alternatively, install from `requirements.txt`, preferably in a virtualenv:

```bash
pip install -r requirements.txt
```

## Usage

Note: make sure you are running within the virtual environment. You can activate it using:

```bash
pipenv shell
```

Notations: in the following `<COLLECTION>` refers to either `CACM` or `CS276`.

### Collection inspection

To inspect a collection and display its key metrics, run:

```bash
python -m inspectcoll <COLLECTION>
```

### Building indexes

To build an index, run:

```bash
python -m indexes build <COLLECTION>
```

The index will be stored in the `cache/` directory and re-used when necessary. You can re-build it by running the above command with the `--force` flag.

Show the size of the index using:

```bash
python -m indexes size <COLLECTION>
```

### Boolean requests

To make a boolean request for `algorithm | artifical` against a collection, use:

```bash
python -m models.boolean <COLLECTION> <QUERY>
```

Example:

```bash
python -m models.boolean CACM "Q('algorithm')"
```

Complete usage:

```bash
$ python -m models.boolean --help
Usage: __main__.py [OPTIONS] COLLECTION QUERY

  Request a collection using the boolean model.

  The query must be a valid Python expression comprised of terms wrapped in
  a `Q` object, and combined using the `|` (OR), `&` (AND) or `~` (NOT)
  operators.

  Examples:

    "Q('research')" => research
    "Q('algorithm') | Q('artificial')" => algorithm OR artificial
    "Q('France') & ~Q('Paris')" => France AND NOT Paris

Options:
  --help  Show this message and exit.
```

### Vector requests

To make a request against a collection using the vector model, use:

```bash
python -m models.vector <COLLECTION> <QUERY>
```

Example:

```bash
python -m models.vector CACM "search algorithm"
```

Complete usage:

```bash
$ python -m models.vector --help
Usage: __main__.py [OPTIONS] COLLECTION QUERY

  Search a collection using the vector model.

Options:
  -k, --topk INTEGER          [default: 10]
  -w, --weighting-scheme WCS  [default: simple]
  --help                      Show this message and exit.
```

### Evaluation

General performance indicators (index build time, request execution time, index size):

```bash
$ python -m evaluation showperfs <COLLECTION>
```

Plot the precision-recall curve for the CACM collection:

```bash
$ python -m evaluation plot
```

R-precision computed on queries for the CACM collection:

```bash
$ python -m evaluation rprec
```

F-measure and E-measure for the CACM collection:

```bash
$ python -m evaluation fe
```

## Credits

Made by Alexandre de Boutray & Florimond Manca.

[python]: https://www.python.org
[pipenv]: https://pipenv.readthedocs.io
