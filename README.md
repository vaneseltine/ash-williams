<p align="center">
  <img src="https://raw.githubusercontent.com/vaneseltine/ash/master/ash-logo.svg" alt="The Ash logo: a blue shirt sleeve leading into a red chainsaw" width=200 />
</p>

<h2 align="center">Ash: finding the Evil Dead in the scientific literature</h2>

> There is an urgent need for reviewers and editorial boards to check the reference list of submitted manuscripts, to prevent the spreading of zombie literature. [(Bucci 2019)](https://doi.org/10.1038/s41419-019-1450-3)

> ‘Zombie papers’ just won’t die. [(Brainard 2022)](https://doi.org/10.1126/science.add6848)

> I'm afraid I'm gonna have to ask you to leave the store. [(Williams 1992)](https://www.imdb.com/title/tt0106308/)

## Usage

This is a work in progress. Get yourself a copy of the Retraction Watch database,
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

## Notebook example

For a full-fledged demonstration, the example notebook downloads the Retraction Watch
database. Set **Ash** loose on your own pasted text or uploaded file.

[![Launch examples/ash_demo.ipynb on Google Colab](https://img.shields.io/badge/launch_notebook-ash_demonstration-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=ff4785)](https://colab.research.google.com/github/vaneseltine/ash-williams/blob/main/examples/ash_demo.ipynb)

## Retraction Watch database

Crossref has licensed the Retraction Watch for a five-year term and are making it public
including updates, per the official announcement: https://doi.org/10.13003/c23rw1d9.
To download the latest data snapshot (~44 MB as of Jul 2024),
simply add your email address to the following URL.
The csv will automatically download:
api.labs.crossref.org/data/retractionwatch?youremailhere@example.com
