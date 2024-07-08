from mimetypes import guess_type

import pytest

from ash import Paper


@pytest.mark.parametrize(
    "path, mimes",
    [
        ("basic_doi_colon_pdf_without_suffix", None),
        ("basic_doi_colon.pdf", "application/pdf"),
        (
            "basic_doi_colon.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        ("basic_doi_colon.rtf", ("application/rtf", "application/msword")),
        ("basic_doi_colon.txt", "text/plain"),
        ("basic_doi_colon.latex", "application/x-latex"),
        ("basic_doi_colon.tex", ("text/x-tex", "application/x-tex")),
    ],
)
def test_mime_implementations_are_covered(path, mimes):
    guessed_mime, _ = guess_type(path)
    assert guessed_mime == mimes or guessed_mime in mimes
    if guessed_mime is not None:
        assert guessed_mime in Paper._MIME_handlers
