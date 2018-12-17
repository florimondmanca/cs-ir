# CS-IR

This repository is home to the code for an *Information Retrieval* (IR) course project.

## Goal

The project aims at implementing various notions of IR such as tokenization, indexing and evaluation, and applying them to real-world text datasets in order to build a rudimentary yet performant search engine.

## Installation

- Place CACM and Stanford text datasets as well as the list of common words into the VCS-ignored `data/` directory, like so:

```
.
├── README.md
├── ...
└── data/
    ├── cacm.all
    ├── common_words.txt
    └── stanford/
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
