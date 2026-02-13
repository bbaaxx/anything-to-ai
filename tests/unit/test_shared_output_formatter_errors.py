"""Unit tests for shared formatter errors."""

from anyfile_to_ai.output_formatter.errors import InvalidPayloadError, InvalidProfileError, UnsupportedFormatError, map_exception


def test_error_codes_are_stable():
    assert UnsupportedFormatError("xml").code == "unsupported_format"
    assert InvalidProfileError("bad-profile").code == "invalid_profile"
    assert InvalidPayloadError("bad payload").code == "invalid_payload"


def test_map_exception_wraps_unknown_exceptions():
    mapped = map_exception(RuntimeError("boom"))
    assert mapped.code == "invalid_payload"
    assert "boom" in mapped.message
