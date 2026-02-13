"""Unit tests for shared markdown formatter behavior."""

import pytest

from anyfile_to_ai.output_formatter.interfaces import format_markdown
from anyfile_to_ai.output_formatter.markdown import format_audio_timestamp
from tests.helpers.output_formatter_fixtures import build_audio_payload, build_pdf_payload


def test_markdown_pdf_heading_and_page_ordering():
    output = format_markdown("pdf", build_pdf_payload())
    assert output.startswith("# PDF Document: doc.pdf")
    assert output.index("## Page 1") < output.index("## Page 2")


def test_markdown_audio_legacy_heading_compatibility_default():
    output = format_markdown("audio", build_audio_payload())
    assert "## [00:00:00.00] Speaker" in output


def test_audio_timestamp_bounds_validation():
    with pytest.raises(Exception):
        format_audio_timestamp(-0.1)
    with pytest.raises(Exception):
        format_audio_timestamp(7200.1)
