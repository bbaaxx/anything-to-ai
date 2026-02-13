"""Integration equivalence checks for text formatter migration."""

from types import SimpleNamespace

from anyfile_to_ai.text_summarizer.__main__ import format_output


def _build_result() -> SimpleNamespace:
    metadata = SimpleNamespace(
        input_length=10,
        chunked=False,
        chunk_count=None,
        detected_language="en",
        processing_time=0.25,
        processing_timestamp="2026-01-01T00:00:00+00:00",
        model_version="test-model",
        configuration={"user_provided": {}, "effective": {}},
        source={"file_path": "unavailable"},
    )
    return SimpleNamespace(summary="A concise summary.", tags=["alpha", "beta", "gamma"], metadata=metadata)


def test_text_formatter_shared_matches_legacy_plain(monkeypatch):
    result = _build_result()

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_TEXT_SHARED", "0")
    legacy = format_output(result, "plain", include_metadata=False)

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_TEXT_SHARED", "1")
    shared = format_output(result, "plain", include_metadata=False)

    assert legacy == shared
