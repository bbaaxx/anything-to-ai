"""Contract tests for unified shared output formatter."""

import json

import pytest

from anyfile_to_ai.output_formatter import format_json, format_markdown, format_output, format_plain
from anyfile_to_ai.output_formatter.errors import InvalidProfileError, UnsupportedFormatError
from tests.helpers.output_formatter_fixtures import build_text_payload


def test_format_route_plain_markdown_json():
    payload = build_text_payload()

    plain = format_output("text", payload, "plain", include_metadata=False)
    markdown = format_output("text", payload, "markdown", include_metadata=False)
    as_json = format_output("text", payload, "json", include_metadata=False)

    assert "SUMMARY:" in plain
    assert "# Summary" in markdown
    parsed = json.loads(as_json)
    assert "output" in parsed


def test_unsupported_format_error_code_is_stable():
    payload = build_text_payload()

    with pytest.raises(UnsupportedFormatError) as exc_info:
        format_output("text", payload, "xml")

    assert exc_info.value.code == "unsupported_format"


def test_endpoint_shims_plain_markdown_json():
    payload = build_text_payload()
    assert "SUMMARY:" in format_plain("text", payload)
    assert "# Summary" in format_markdown("text", payload)

    response = json.loads(format_json("text", payload, include_metadata=True))
    assert "output" in response


def test_metadata_normalization_contract_for_include_metadata():
    payload = build_text_payload()
    response = json.loads(format_json("text", payload, include_metadata=True))

    assert "metadata" in response
    assert "extensions" in response["metadata"]
    assert response["metadata"]["extensions"]["custom_key"] == "custom-value"


def test_invalid_profile_error_contract():
    payload = build_text_payload()
    with pytest.raises(InvalidProfileError) as exc_info:
        format_plain("not-a-profile", payload)

    assert exc_info.value.code == "invalid_profile"
