"""Unit tests for summarizer models."""

import pytest
from pydantic import ValidationError
from anything_to_ai.text_summarizer.models import (
    SummaryRequest,
    SummaryResult,
    SummaryMetadata,
    TextChunk,
)


class TestSummaryRequest:
    """Unit tests for SummaryRequest model."""

    def test_valid_request(self):
        """Test creating valid SummaryRequest."""
        req = SummaryRequest(text="Test content")
        assert req.text == "Test content"
        assert req.format == "json"
        assert req.include_metadata is True

    def test_empty_text_raises_error(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError):
            SummaryRequest(text="")

    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises error."""
        with pytest.raises(ValidationError, match="Text must not be empty"):
            SummaryRequest(text="   \n\t  ")

    def test_custom_format(self):
        """Test setting custom format."""
        req = SummaryRequest(text="Test", format="plain")
        assert req.format == "plain"

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises error."""
        with pytest.raises(ValidationError):
            SummaryRequest(text="Test", format="xml")

    def test_metadata_flag(self):
        """Test setting include_metadata flag."""
        req = SummaryRequest(text="Test", include_metadata=False)
        assert req.include_metadata is False


class TestSummaryResult:
    """Unit tests for SummaryResult model."""

    def test_valid_result(self):
        """Test creating valid SummaryResult."""
        result = SummaryResult(summary="Test summary", tags=["tag1", "tag2", "tag3"])
        assert result.summary == "Test summary"
        assert len(result.tags) == 3

    def test_empty_summary_raises_error(self):
        """Test that empty summary raises error."""
        with pytest.raises(ValidationError):
            SummaryResult(summary="", tags=["tag1", "tag2", "tag3"])

    def test_less_than_three_tags_raises_error(self):
        """Test that fewer than 3 tags raises error."""
        with pytest.raises(ValidationError):
            SummaryResult(summary="Test", tags=["tag1", "tag2"])

    def test_empty_tag_raises_error(self):
        """Test that empty tags raise error."""
        with pytest.raises(ValidationError, match="Tags must be non-empty"):
            SummaryResult(summary="Test", tags=["tag1", "", "tag3"])

    def test_whitespace_tag_raises_error(self):
        """Test that whitespace-only tags raise error."""
        with pytest.raises(ValidationError, match="Tags must be non-empty"):
            SummaryResult(summary="Test", tags=["tag1", "   ", "tag3"])

    def test_metadata_optional(self):
        """Test that metadata is optional."""
        result = SummaryResult(summary="Test", tags=["t1", "t2", "t3"])
        assert result.metadata is None

    def test_with_metadata(self):
        """Test result with metadata."""
        metadata = SummaryMetadata(input_length=100, chunked=False, processing_time=1.5)
        result = SummaryResult(summary="Test", tags=["t1", "t2", "t3"], metadata=metadata)
        assert result.metadata is not None
        assert result.metadata.input_length == 100


class TestSummaryMetadata:
    """Unit tests for SummaryMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        meta = SummaryMetadata(input_length=100, chunked=False, processing_time=1.5)
        assert meta.input_length == 100
        assert meta.chunked is False
        assert meta.processing_time == 1.5

    def test_zero_input_length_raises_error(self):
        """Test that zero input_length raises error."""
        with pytest.raises(ValidationError):
            SummaryMetadata(input_length=0, chunked=False, processing_time=1.0)

    def test_negative_input_length_raises_error(self):
        """Test that negative input_length raises error."""
        with pytest.raises(ValidationError):
            SummaryMetadata(input_length=-10, chunked=False, processing_time=1.0)

    def test_negative_processing_time_raises_error(self):
        """Test that negative processing_time raises error."""
        with pytest.raises(ValidationError):
            SummaryMetadata(input_length=100, chunked=False, processing_time=-1.0)

    def test_chunked_requires_chunk_count(self):
        """Test that chunked=True requires chunk_count."""
        with pytest.raises(ValidationError, match="chunk_count required"):
            SummaryMetadata(input_length=100, chunked=True, chunk_count=None, processing_time=1.0)

    def test_chunked_with_chunk_count(self):
        """Test metadata with chunking."""
        meta = SummaryMetadata(input_length=15000, chunked=True, chunk_count=2, processing_time=5.0)
        assert meta.chunked is True
        assert meta.chunk_count == 2

    def test_detected_language_optional(self):
        """Test that detected_language is optional."""
        meta = SummaryMetadata(input_length=100, chunked=False, processing_time=1.0)
        assert meta.detected_language is None

    def test_with_detected_language(self):
        """Test metadata with detected language."""
        meta = SummaryMetadata(input_length=100, chunked=False, detected_language="en", processing_time=1.0)
        assert meta.detected_language == "en"


class TestTextChunk:
    """Unit tests for TextChunk model."""

    def test_valid_chunk(self):
        """Test creating valid chunk."""
        chunk = TextChunk(index=0, content="Test content", start_word=0, end_word=2)
        assert chunk.index == 0
        assert chunk.content == "Test content"
        assert chunk.start_word == 0
        assert chunk.end_word == 2

    def test_negative_index_raises_error(self):
        """Test that negative index raises error."""
        with pytest.raises(ValidationError):
            TextChunk(index=-1, content="Test", start_word=0, end_word=1)

    def test_empty_content_raises_error(self):
        """Test that empty content raises error."""
        with pytest.raises(ValidationError):
            TextChunk(index=0, content="", start_word=0, end_word=1)

    def test_negative_start_word_raises_error(self):
        """Test that negative start_word raises error."""
        with pytest.raises(ValidationError):
            TextChunk(index=0, content="Test", start_word=-1, end_word=1)

    def test_end_word_less_than_start_raises_error(self):
        """Test that end_word <= start_word raises error."""
        with pytest.raises(ValidationError, match="end_word must be greater than start_word"):
            TextChunk(index=0, content="Test", start_word=10, end_word=10)

        with pytest.raises(ValidationError, match="end_word must be greater than start_word"):
            TextChunk(index=0, content="Test", start_word=10, end_word=5)
