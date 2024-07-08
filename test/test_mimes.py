import pytest

from ash.ash import path_to_mime_type


@pytest.mark.parametrize(
    "filename, acceptable_mimes",
    [
        (
            "basic_doi_colon.pdf",
            ("application/pdf"),
        ),
        (
            "pdf_without_suffix",
            ("application/pdf"),
        ),
        (
            "basic_doi_colon.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        (
            "basic_doi_colon.rtf",
            ("application/rtf", "application/msword"),
        ),
        (
            "basic_doi_colon.txt",
            ("text/plain"),
        ),
        (
            "basic_doi_colon.latex",
            ("application/x-latex"),
        ),
        (
            "basic_doi_colon.tex",
            ("text/x-tex", "application/x-tex"),
        ),
    ],
)
def test_mimes_detected_from_vault(vault, filename, acceptable_mimes):
    path = vault[filename]
    guessed_mime = path_to_mime_type(path)
    assert guessed_mime in acceptable_mimes
