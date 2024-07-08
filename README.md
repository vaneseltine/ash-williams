# ash

Hunting Deadites in the references

# Formats

Eventually, in approximately this order:

- [x] PDF (ideally generated from multiple sources) - pypdf
- [x] DOCX - builtin xml (PPTX too?) https://stackoverflow.com/a/20663596/7846185
- [x] Text (covers TEX, BIB, etc) - no conversion required
- [x] RTF (fourth format PNAS accepts) - https://github.com/joshy/striprtf standalone

If we're adding dependencies, we should maybe lazy load required libraries
or have as optional on install.

Microsoft Word DOC has been obsolete since 2007, so we aren't supporting it.

# Reporting

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

# Demo

This could be a web app, sure, but we could start with just a binder/colab notebook.

# Retraction Watch via Crossref

https://doi.org/10.13003/c23rw1d9

## CSV

https://api.labs.crossref.org/data/retractionwatch?matvan@umich.edu

It's 44 MB so not enormous but not an insignificant amount to deal with.

We could maybe just include the raw DOIs in the package, how big is that?

- Nnnnnn, well, we want to report the RW info as well.

## API

We could alternatively hit the Crossref API with DOIs in hand

- No, they prefer we instead pull down in bulk so we don't hit repeatedly
- Could consider going from the Crossref end rather than the RW CSV however?

- https://api.labs.crossref.org/works/10.1016/S0140-6736(14)60921-1?mailto=matvan@umich.edu
- https://api.labs.crossref.org/works/10.1016/S2213-2600(14)70125-0?mailto=matvan@umich.edu (cited in Cagney)

# Discussion of citation practice & policy

COPE Case number 15-17, "Citing a retracted paper," https://publicationethics.org/case/citing-retracted-paper:

> They are presumably asking whether a paper citing a retracted paper is to be considered sound? We think this should be a question for the peer reviewers. Perhaps, as a responsible editor, they should point out to the reviewers that one of the references has been retracted. The reviewers could then decide whether this was a key reference supporting the crux of the current paper or whether it was merely something that could be deleted or replaced with something more suitable.

> On the somewhat more philosophical question of whether a retracted paper should ever be cited, there may be legitimate cases where one would want to cite a retracted article. It comes down to why you cite something; as a way of noting something that happened previously, would be fine. If writing a paper about retractions, for example, one might quite reasonably want to cite some key retracted papers to illustrate the issues involved. However, it is very important to mark the paper as retracted in the reference section so this is clearly marked for readers (eg, Author AB, et al. RETRACTED: Title of article. Journal name. 2015, 100: 1-7.)
