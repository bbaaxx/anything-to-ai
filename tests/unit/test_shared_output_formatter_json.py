"""Unit tests for shared JSON formatter behavior."""

import json

from anyfile_to_ai.output_formatter.interfaces import format_json
from tests.helpers.output_formatter_fixtures import build_text_payload


def test_json_output_has_required_output_field():
    payload = build_text_payload()
    parsed = json.loads(format_json("text", payload, include_metadata=False))

    assert "output" in parsed
    assert "metadata" not in parsed


def test_json_include_metadata_flag_is_enforced():
    payload = build_text_payload()
    with_metadata = json.loads(format_json("text", payload, include_metadata=True))
    without_metadata = json.loads(format_json("text", payload, include_metadata=False))

    assert "metadata" in with_metadata
    assert "metadata" not in without_metadata


def test_json_serialization_is_deterministic():
    payload = build_text_payload()
    first = format_json("text", payload, include_metadata=True)
    second = format_json("text", payload, include_metadata=True)
    assert first == second
