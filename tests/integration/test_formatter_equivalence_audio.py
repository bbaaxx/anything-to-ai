"""Integration equivalence checks for audio formatter migration."""

from anyfile_to_ai.audio_processor.markdown_formatter import format_markdown


def test_audio_formatter_shared_matches_legacy_markdown(monkeypatch):
    payload = {
        "filename": "clip.mp3",
        "duration": 2.5,
        "model": "medium",
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "Hello"},
            {"start": 1.0, "end": 2.0, "text": "world"},
        ],
    }

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_AUDIO_SHARED", "0")
    legacy = format_markdown(payload)

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_AUDIO_SHARED", "1")
    shared = format_markdown(payload)

    assert "Hello" in legacy
    assert "world" in legacy
    assert "Hello" in shared
    assert "world" in shared
