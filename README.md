# ash

Hunting the [evil dead](https://www.science.org/content/article/zombie-papers-wont-die-retracted-papers-notorious-fraudster-still-cited-years-later) in the scientific literature.

This is a work heavily in progress. It will be soon be available via:

```
python -m pip install ash-williams
```

And a simple use looks like:

```python
from ash import Paper
paper = Paper("sample.pdf")
print(paper.report(db="./retraction_watch.csv"))
```

# Notes

## Formats

- [x] PDF (ideally generated from multiple sources) - pypdf
- [x] DOCX - builtin xml (PPTX too?) https://stackoverflow.com/a/20663596/7846185
- [x] Text (covers TEX, BIB, etc) - no conversion required
- [x] RTF (fourth format PNAS accepts) - https://github.com/joshy/striprtf standalone

Microsoft Word DOC has been obsolete since 2007, so we aren't supporting it.

## Reporting

Do we want to give...

- Page number (pdf/word)?
- Line number (text)?
- Stringed context with highlighting?
- Retraction watch records: for each entry
  - Sort by date
  - RetractionNature
  - RetractionDate -- change from datetime
  - RetractionDOI
  - RetractionReasons?

## Demo

- [ ] Server in separate repository (in progress)
- [ ] Binder/colab notebook for easy Python sampling

## Retraction Watch via Crossref

Per the official Crossref announcement -- https://doi.org/10.13003/c23rw1d9 -- to download the latest data snapshot (~44 MB as of Jul 2024), add your email address to the following: api.labs.crossref.org/data/retractionwatch?youremailhere@example.com

### API

We could alternatively hit the Crossref API with DOIs in hand

- No, they prefer we instead pull down in bulk so we don't hit repeatedly
- Could consider going from the Crossref end rather than the RW CSV however?

- https://api.labs.crossref.org/works/10.1016/S0140-6736(14)60921-1?mailto=matvan@umich.edu
- https://api.labs.crossref.org/works/10.1016/S2213-2600(14)70125-0?mailto=matvan@umich.edu (cited in Cagney)

## Discussion of citation practice & policy

COPE Case number 15-17, "Citing a retracted paper," https://publicationethics.org/case/citing-retracted-paper:

> They are presumably asking whether a paper citing a retracted paper is to be considered sound? We think this should be a question for the peer reviewers. Perhaps, as a responsible editor, they should point out to the reviewers that one of the references has been retracted. The reviewers could then decide whether this was a key reference supporting the crux of the current paper or whether it was merely something that could be deleted or replaced with something more suitable.

> On the somewhat more philosophical question of whether a retracted paper should ever be cited, there may be legitimate cases where one would want to cite a retracted article. It comes down to why you cite something; as a way of noting something that happened previously, would be fine. If writing a paper about retractions, for example, one might quite reasonably want to cite some key retracted papers to illustrate the issues involved. However, it is very important to mark the paper as retracted in the reference section so this is clearly marked for readers (eg, Author AB, et al. RETRACTED: Title of article. Journal name. 2015, 100: 1-7.)
