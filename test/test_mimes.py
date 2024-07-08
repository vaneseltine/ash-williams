from mimetypes import guess_type

import pytest


@pytest.mark.parametrize(
    "path, mime",
    [
        ("basic_doi_colon_pdf_without_suffix", None),
        ("basic_doi_colon.pdf", "application/pdf"),
        (
            "basic_doi_colon.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        ("basic_doi_colon.rtf", "application/rtf"),
        ("basic_doi_colon.txt", "text/plain"),
        ("basic_doi_colon.latex", "application/x-latex"),
        ("basic_doi_colon.tex", "text/x-tex"),
    ],
)
def test_whether_mimes_work(path, mime):
    guessed_mime, _ = guess_type(path)
    assert guessed_mime == mime
