"""Contract tests for Text summarizer metadata extension."""

import pytest


class TestSummaryMetadataExtension:
    """Test SummaryMetadata extension with universal fields."""

    def test_summary_result_metadata_can_be_none(self):
        from anyfile_to_ai.text_summarizer.models import SummaryResult

        result = SummaryResult(summary="Test summary", tags=["tag1", "tag2", "tag3"], metadata=None)
        assert result.metadata is None

    def test_summary_metadata_has_existing_fields(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=5000,
            chunked=True,
            chunk_count=5,
            detected_language="en",
            processing_time=3.2,
        )

        assert metadata.input_length == 5000
        assert metadata.chunked is True
        assert metadata.chunk_count == 5
        assert metadata.detected_language == "en"
        assert metadata.processing_time == 3.2

    def test_summary_metadata_has_universal_fields(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=5000,
            chunked=True,
            chunk_count=5,
            detected_language="en",
            processing_time=3.2,
            processing_timestamp="2025-10-25T14:45:00+00:00",
            model_version="llama2",
            configuration={
                "user_provided": {"model": "llama2"},
                "effective": {"model": "llama2", "max_tokens": 4096},
            },
            source={
                "file_path": "article.txt",
                "file_size_bytes": 102400,
                "input_length_words": 5000,
                "input_length_chars": 30000,
                "detected_language": "en",
                "chunked": True,
                "chunk_count": 5,
            },
        )

        assert hasattr(metadata, "processing_timestamp")
        assert hasattr(metadata, "model_version")
        assert hasattr(metadata, "configuration")
        assert hasattr(metadata, "source")

        assert metadata.processing_timestamp == "2025-10-25T14:45:00+00:00"
        assert metadata.model_version == "llama2"
        assert metadata.configuration["user_provided"]["model"] == "llama2"
        assert metadata.source["file_path"] == "article.txt"

    def test_summary_metadata_universal_fields_are_optional(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=5000,
            chunked=False,
            chunk_count=None,
            detected_language="en",
            processing_time=2.0,
        )

        assert metadata.processing_timestamp is None
        assert metadata.model_version is None
        assert metadata.configuration is None
        assert metadata.source is None

    def test_summary_metadata_stdin_source_handling(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=3000,
            chunked=False,
            chunk_count=None,
            detected_language="en",
            processing_time=2.5,
            processing_timestamp="2025-10-25T14:45:00+00:00",
            model_version="llama2",
            source={
                "file_path": "unavailable",
                "file_size_bytes": "unavailable",
                "input_length_words": 3000,
                "input_length_chars": 18000,
                "detected_language": "en",
                "chunked": False,
                "chunk_count": None,
            },
        )

        assert metadata.source["file_path"] == "unavailable"
        assert metadata.source["file_size_bytes"] == "unavailable"
        assert metadata.source["input_length_words"] == 3000


class TestBackwardCompatibility:
    """Test that existing SummaryMetadata behavior is preserved."""

    def test_old_metadata_structure_still_works(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata, SummaryResult

        old_metadata = SummaryMetadata(input_length=1000, chunked=False, chunk_count=None, detected_language="en", processing_time=1.5)

        result = SummaryResult(summary="Test", tags=["a", "b", "c"], metadata=old_metadata)

        assert result.metadata.input_length == 1000
        assert result.metadata.chunked is False
        assert result.metadata.processing_time == 1.5

    def test_new_fields_dont_break_existing_code(self):
        from anyfile_to_ai.text_summarizer.models import SummaryMetadata

        metadata = SummaryMetadata(
            input_length=2000,
            chunked=True,
            chunk_count=3,
            detected_language="en",
            processing_time=2.0,
            processing_timestamp="2025-10-25T14:45:00+00:00",
            model_version="llama2",
        )

        assert metadata.input_length == 2000
        assert metadata.processing_timestamp == "2025-10-25T14:45:00+00:00"
