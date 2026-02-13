"""Unit tests for shared plain formatter behavior."""

from anyfile_to_ai.output_formatter.interfaces import format_plain
from tests.helpers.output_formatter_fixtures import build_audio_payload, build_text_payload


def test_plain_text_profile_parity_shape():
    output = format_plain("text", build_text_payload())
    assert "SUMMARY:" in output
    assert "TAGS:" in output
    assert "- alpha" in output


def test_plain_audio_segments_include_timestamps_when_present():
    payload = build_audio_payload()
    payload["segments"][0]["display_timestamp"] = "00:00:00.00"
    payload["segments"][1]["display_timestamp"] = "00:00:01.20"

    output = format_plain("audio", payload)
    assert "[00:00:00.00] Hello" in output
    assert "[00:00:01.20] world" in output
