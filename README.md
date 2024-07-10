# ash

Hunting the [evil dead](https://www.science.org/content/article/zombie-papers-wont-die-retracted-papers-notorious-fraudster-still-cited-years-later) in the scientific literature.

This is a work in progress. Try it via:

```
python -m pip install ash-williams
```

And a simple use looks like:

```python
from ash import Paper

paper = Paper("sample.pdf")
print(paper.report(db="./retraction_watch.csv"))
```
