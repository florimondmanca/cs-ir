# CS-IR

This repository is home to the code for an _Information Retrieval_ (IR) course project.

## Goal

The project aims at implementing various notions of IR such as tokenization, indexing and evaluation, and applying them to real-world text datasets in order to build a rudimentary yet performant search engine.

## Installation

- Place the CACM and CS276 datasets on your computer, then create a `.env` file with the following variables:

```dotenv
DATA_STOP_WORDS_PATH=path/to/common_words.txt
DATA_CACM_PATH=path/to/cacm.all
DATA_CS276_PATH=/path/to/pa1-data
```

- Get [Python] 3.6+ and [Pipenv] and install dependencies:

```bash
pipenv install
```

## Usage

Note: make sure you are running within the virtual environment. You can activate it using:

```bash
pipenv shell
```

### Collection inspection

To inspect a collection and display its key metrics, run:

```python
python -m inspectcoll <COLLECTION>
# Example:
python -m inspectcoll CACM
```

### Building indexes

To build an index, run:

```python
python -m indexes build <COLLECTION>
# Example:
python -m indexes build CACM
```

The index will be stored in the `cache/` directory and re-used when necessary. You can re-build it by running the above command with the `--force` flag.

### Boolean requests

To make a boolean request for `algorithm | artifical` against a collection, use:

```python
python -m models.boolean <COLLECTION>
# Example:
python -m models.boolean CACM
```

Complete usage:

```bash
$ python -m models.boolean --help
Usage: boolean.py [OPTIONS] COLLECTION

  Test the boolean model on a collection.

Options:
  --help  Show this message and exit.
```

## Credits

Made by Alexandre de Boutray & Florimond Manca.

[python]: https://www.python.org
[pipenv]: https://pipenv.readthedocs.io
