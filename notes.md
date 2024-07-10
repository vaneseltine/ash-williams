# Notes

## TODO

- [x] PDF extracts
- [x] DOCX extracts
- [x] Text extracts
- [x] RTF extracts
- [x] Implement lazy validation of DOI via doi.org APIs
- [ ] Address partial DOI extracts from PDF split text fields
- [ ] Consider DOI validation to improve accurate extraction

## Live validation of DOI

Valid: https://doi.org/api/handles/10.1177/0020720920940575

```json
{
  "responseCode": 1,
  "handle": "10.1177/0020720920940575",
  "values": [
    {
      "index": 1,
      "type": "URL",
      "data": {
        "format": "string",
        "value": "http://journals.sagepub.com/doi/10.1177/0020720920940575"
      },
      "ttl": 86400,
      "timestamp": "2020-07-29T04:52:30Z"
    },
    {
      "index": 700050,
      "type": "700050",
      "data": {
        "format": "string",
        "value": "2020072821515400292"
      },
      "ttl": 86400,
      "timestamp": "2020-07-29T04:52:30Z"
    },
    {
      "index": 100,
      "type": "HS_ADMIN",
      "data": {
        "format": "admin",
        "value": {
          "handle": "0.na/10.1177",
          "index": 200,
          "permissions": "111111110010"
        }
      },
      "ttl": 86400,
      "timestamp": "2020-07-29T04:52:30Z"
    }
  ]
}
```

Or narrow down requested "type" but that's probably not important

Valid, URL only: https://doi.org/api/handles/10.1177/0020720920940575?type=URL

```json
{
  "responseCode": 1,
  "handle": "10.1177/0020720920940575",
  "values": [
    {
      "index": 1,
      "type": "URL",
      "data": {
        "format": "string",
        "value": "http://journals.sagepub.com/doi/10.1177/0020720920940575"
      },
      "ttl": 86400,
      "timestamp": "2020-07-29T04:52:30Z"
    }
  ]
}
```

Probably all that matters is we don't get the invalid response.

Invalid: https://doi.org/api/handles/10.1177/5555555555555555

```json
{
  "responseCode": 100,
  "handle": "10.1177/5555555555555555"
}
```

https://www.doi.org/the-identifier/resources/factsheets/doi-resolution-documentation

>     Response Codes
>
>     1 : Success. (HTTP 200 OK)
>     2 : Error. Something unexpected went wrong during handle resolution. (HTTP 500 Internal Server Error)
>     100 : Handle Not Found. (HTTP 404 Not Found)
>     200 : Values Not Found. The handle exists but has no values (or no values according to the types and indices specified). (HTTP 200 OK)

## Formats

- PDF (ideally generated from multiple sources) - pypdf
- DOCX - builtin xml (PPTX too?) https://stackoverflow.com/a/20663596/7846185
- Text (covers TEX, BIB, etc) - no conversion required
- RTF (fourth format PNAS accepts) - https://github.com/joshy/striprtf standalone
- Microsoft Word DOC has been obsolete since 2007, so we aren't supporting it.

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

### Analogous use of RW database at Wikipedia

https://en.wikipedia.org/wiki/Wikipedia:Wikipedia_Signpost/2024-06-08/Special_report
