"""Integration equivalence checks for PDF formatter migration."""

from anyfile_to_ai.pdf_extractor.markdown_formatter import format_markdown


def test_pdf_formatter_shared_matches_legacy_markdown(monkeypatch):
    payload = {
        "filename": "doc.pdf",
        "pages": [
            {"number": 1, "text": "Page one."},
            {"number": 2, "text": "Page two."},
        ],
    }

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_PDF_SHARED", "0")
    legacy = format_markdown(payload)

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_PDF_SHARED", "1")
    shared = format_markdown(payload)

    assert legacy == shared
