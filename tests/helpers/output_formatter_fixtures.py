"""Shared fixture builders for output formatter tests."""

from typing import Any


def build_common_metadata() -> dict[str, Any]:
    return {
        "processing": {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "model_version": "test-model",
            "processing_time_seconds": 0.42,
        },
        "configuration": {
            "user_provided": {"format": "json"},
            "effective": {"format": "json", "include_metadata": True},
        },
        "source": {
            "file_path": "/tmp/input.txt",
        },
        "custom_key": "custom-value",
    }


def build_text_payload() -> dict[str, Any]:
    return {
        "content": "A concise summary.",
        "tags": ["alpha", "beta", "gamma"],
        "metadata": build_common_metadata(),
    }


def build_audio_payload() -> dict[str, Any]:
    return {
        "content": "Transcribed content",
        "segments": [
            {"start": 0.0, "end": 1.2, "text": "Hello"},
            {"start": 1.2, "end": 2.6, "text": "world"},
        ],
        "metadata": build_common_metadata(),
    }


def build_pdf_payload() -> dict[str, Any]:
    return {
        "content": "PDF fallback content",
        "filename": "doc.pdf",
        "pages": [
            {"number": 1, "text": "Page one."},
            {"number": 2, "text": "Page two."},
        ],
        "metadata": build_common_metadata(),
    }
