# ash

Hunting Deadites in the references

# Formats

Eventually, in approximately this order:

- [ ] PDF (ideally generated from multiple sources) - pypdf
- [ ] DOCX - builtin xml (PPTX too?) https://stackoverflow.com/a/20663596/7846185
- [ ] Text (covers TEX, BIB, etc) - no conversion required
- [ ] RTF (fourth format PNAS accepts) - https://github.com/joshy/striprtf standalone
- [ ] DOC - https://github.com/decalage2/oletools might also cover RTF, ~4.5mb 8 pack

If we're adding dependencies, we should maybe lazy load required libraries
or have as optional on install.

# Reporting

Do we want to give...

- Page number (pdf/word)?
- Line number (text)?
- Stringed context with highlighting?

# Demo

This could be a web app, sure, but we could start with just a binder/colab notebook.

# Retraction Watch DB via Crossref

https://doi.org/10.13003/c23rw1d9

https://api.labs.crossref.org/data/retractionwatch?name@email.org

We could maybe just include the raw DOIs in the package, how big is that?

- Eh, but no we want to report the RW info as well.
