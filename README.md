<p align="center">
  <img src="https://raw.githubusercontent.com/vaneseltine/ash/master/ash-logo.svg" alt="The Ash logo: a blue shirt sleeve leading into a red chainsaw" width=200 />
</p>

<h2 align="center">Ash: finding the Evil Dead in the scientific literature</h2>

> There is an urgent need for reviewers and editorial boards to check the reference list
> of submitted manuscripts, to prevent the spreading of zombie literature.
> [(Bucci 2019)](https://doi.org/10.1038/s41419-019-1450-3)

> ‘Zombie papers’ just won’t die.
> [(Brainard 2022)](https://doi.org/10.1126/science.add6848)

> I'm afraid I'm gonna have to ask you to leave the store.
> [(Williams 1992)](https://www.imdb.com/title/tt0106308/)

## Demo website

I've thrown together https://matvan.pythonanywhere.com as a basic demo of Ash,
so you can get a sense of what we're talking about here.

## Python package

> [!WARNING]
> This is a work in progress. The API is subject to change.

Get yourself a copy of the [Retraction Watch database](#retraction-watch-database),
get yourself a paper with some references in it,
then try **Ash**.

First install:

```bash
python -m pip install ash-williams
```

And then something like:

```python
from pprint import pprint

import ash

db = ash.RetractionDatabase("./retractions.csv")
paper = ash.Paper.from_path("./manuscript.docx")
pprint(paper.report(db))
```

A rudimentary command line interface is currently included for your convenience:

```
$ ash
Usage: ash [OPTIONS] [PAPER]

  Simple program that runs Ash on PAPER using DATABASE.

Options:
  --database PATH  Path to retractions database file.
  --clear          Clear path to database file.
  --help           Show this message and exit.

$ ash --database ./retractions.csv
Database path: ./retractions.csv

$ ash questionable_paper.docx
Database path: ./retractions.csv
{'dois': {'10.21105/joss.03440': {'Retracted': False}}, 'zombies': []}
```

The path of the database persists between sessions, so you'll likely need to specify it
only the once.

### Cloud Notebook

For a full-fledged demonstration without any need to install on your own machine,
examine this example notebook through Google Colab.

- Installs **Ash** in cloud-hosted notebook.
- Provided your email, downloads the Retraction Watch database.
- Runs and reports on a block of text -- or your uploaded file.

[![Launch examples/ash_demo.ipynb on Google Colab](https://img.shields.io/badge/jupyter_notebook-launch_on_mybinder.org-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=df8429)](https://mybinder.org/v2/gh/vaneseltine/ash-williams/HEAD?labpath=examples%2Fash_demo.ipynb)

[![Launch examples/ash_demo.ipynb on Google Colab](https://img.shields.io/badge/jupyter_notebook-launch_on_google_colab-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=f9ab00)](https://colab.research.google.com/github/vaneseltine/ash-williams/blob/main/examples/ash_demo.ipynb)

## Retraction Watch database

Crossref has licensed the Retraction Watch for a five-year term and are making it public
including updates, per the official announcement: https://doi.org/10.13003/c23rw1d9.
To download the latest data snapshot (~44 MB as of Jul 2024),
simply add your email address to the following URL.
The csv will automatically download:
api.labs.crossref.org/data/retractionwatch?youremailhere@example.com

The official home of Retraction Watch appears,
at least as of July 2024,
to continue to be [retractiondatabase.org](http://retractiondatabase.org).
