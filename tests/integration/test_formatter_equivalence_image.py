"""Integration equivalence checks for image formatter migration."""

from anyfile_to_ai.image_processor.cli import format_output
from anyfile_to_ai.image_processor.models import DescriptionResult, ProcessingResult


def _build_result() -> ProcessingResult:
    item = DescriptionResult(
        image_path="/tmp/test.jpg",
        description="A test image.",
        confidence_score=0.95,
        processing_time=0.2,
        model_used="test-model",
        prompt_used="prompt",
        success=True,
        metadata={
            "processing": {"timestamp": "2026-01-01T00:00:00+00:00", "model_version": "test-model", "processing_time_seconds": 0.2},
            "configuration": {"user_provided": {}, "effective": {}},
            "source": {"file_path": "/tmp/test.jpg"},
        },
    )
    return ProcessingResult(success=True, results=[item], total_images=1, successful_count=1, failed_count=0, total_processing_time=0.2)


def test_image_formatter_shared_matches_legacy_markdown(monkeypatch):
    result = _build_result()

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_IMAGE_SHARED", "0")
    legacy = format_output(result, "markdown")

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_IMAGE_SHARED", "1")
    shared = format_output(result, "markdown")

    assert "# Image Descriptions" in legacy
    assert "# Image Descriptions" in shared
    assert "A test image." in legacy
    assert "A test image." in shared
