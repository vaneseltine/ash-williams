# ash
Hunting Deadites in the references

# Formats
Eventually, in approximately this order:
- [ ] PDF (ideally generated from multiple sources) - pypdf
- [ ] DOCX - builtin xml (PPTX too?) https://stackoverflow.com/a/20663596/7846185
- [ ] Text (covers TEX, BIB, etc) - no conversion required
- [ ] RTF (fourth format PNAS accepts) - https://github.com/joshy/striprtf
- [ ] DOC - https://github.com/decalage2/oletools might also cover RTF, might be more cumbersome

If we're adding dependencies, we should maybe lazy load required libraries or have as optional on install.

# Demo
This could be a web app, sure, but we could start with just a binder/colab notebook.
