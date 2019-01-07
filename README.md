# CS-IR

This repository is home to the code for an *Information Retrieval* (IR) course project.

## Goal

The project aims at implementing various notions of IR such as tokenization, indexing and evaluation, and applying them to real-world text datasets in order to build a rudimentary yet performant search engine.

## Installation

- Place the CACM, CS276 and Stanford datasets on your computer, then create a `.env` file with the following variables:

```dotenv
DATA_STOP_WORDS_PATH=path/to/common_words.txt
DATA_CACM_PATH=path/to/cacm.all
```

- Get [Python] (3.6+) and [Pipenv] and install dependencies:

```bash
pipenv install
```

## Quick start

You can run the main script (but this is bound to change):

```bash
python main.py
```

Watch for plots and the output in the console.

## Credits

Made by Alexandre de Boutray & Florimond Manca.

[Python]: https://www.python.org
[Pipenv]: https://pipenv.readthedocs.io
