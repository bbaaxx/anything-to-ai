"""Unit tests for shared metadata normalization."""

from anyfile_to_ai.output_formatter.metadata import normalize_metadata
from tests.helpers.output_formatter_fixtures import build_common_metadata


def test_normalize_metadata_keeps_required_groups():
    normalized = normalize_metadata(build_common_metadata())

    assert set(normalized) == {"processing", "configuration", "source", "extensions"}
    assert normalized["processing"]["timestamp"] == "2026-01-01T00:00:00+00:00"
    assert normalized["source"]["file_path"] == "/tmp/input.txt"


def test_normalize_metadata_preserves_unknown_keys_in_extensions():
    normalized = normalize_metadata(build_common_metadata())

    assert normalized["extensions"]["custom_key"] == "custom-value"


def test_normalize_metadata_none_passthrough():
    assert normalize_metadata(None) is None
