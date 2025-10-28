"""Integration test for Text summarizer backward compatibility."""

import json
from datetime import datetime, timezone

import pytest


class TestTextMetadataBackwardCompatibility:
    """Tests ensuring text summarizer metadata is backward compatible."""

    def test_summary_result_preserves_existing_fields(self):
        """Test SummaryResult preserves all existing fields."""
        from anyfile_to_ai.text_summarizer.models import SummaryResult, SummaryMetadata

        metadata = SummaryMetadata(
            input_length=100,
            chunked=False,
            chunk_count=None,
            detected_language="en",
            processing_time=2.5,
            processing_timestamp="2025-10-25T14:30:00+00:00",
            model_version="llama2",
            configuration={"user_provided": {}, "effective": {}},
            source={"file_path": "/test.txt", "file_size_bytes": 1024, "input_length_words": 20, "input_length_chars": 100, "detected_language": "en", "chunked": False, "chunk_count": None},
        )

        result = SummaryResult(summary="Test summary", tags=["test", "sample", "demo"], metadata=metadata)

        assert result.summary == "Test summary"
        assert len(result.tags) == 3
        assert result.metadata.input_length == 100
        assert result.metadata.processing_time == 2.5

    def test_summary_metadata_json_serialization(self):
        """Test SummaryMetadata serializes to JSON correctly."""
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=150,
            chunked=True,
            chunk_count=3,
            detected_language="en",
            processing_time=3.0,
            processing_timestamp="2025-10-25T14:30:00+00:00",
            model_version="mistral",
            configuration={"user_provided": {"model": "mistral"}, "effective": {"model": "mistral", "provider": "ollama"}},
            source={"file_path": "/doc.txt", "file_size_bytes": 2048, "input_length_words": 30, "input_length_chars": 150, "detected_language": "en", "chunked": True, "chunk_count": 3},
        )

        metadata_dict = metadata.model_dump()
        json_str = json.dumps(metadata_dict)
        parsed = json.loads(json_str)

        assert parsed["input_length"] == 150
        assert parsed["processing_timestamp"] == "2025-10-25T14:30:00+00:00"

    def test_extended_metadata_optional_fields(self):
        """Test extended metadata fields are optional."""
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(input_length=50, chunked=False, chunk_count=None, detected_language=None, processing_time=1.0)

        assert metadata.processing_timestamp is None
        assert metadata.model_version is None
        assert metadata.configuration is None
        assert metadata.source is None
