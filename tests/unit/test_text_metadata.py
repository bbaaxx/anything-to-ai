"""Unit tests for Text metadata extraction."""

import os
from datetime import datetime, timezone, UTC
from unittest.mock import patch

import pytest

from anyfile_to_ai.text_summarizer.metadata import (
    _extract_text_source_metadata,
    extract_text_metadata,
)


class TestTextMetadataExtraction:
    """Tests for text metadata extraction."""

    def test_extract_text_metadata_complete(self, tmp_path):
        """Test complete text metadata extraction."""
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document with multiple words for testing."
        test_file.write_text(test_content)

        user_config = {"model": "llama2"}
        effective_config = {"model": "llama2", "provider": "ollama"}

        result = extract_text_metadata(
            text=test_content,
            file_path=str(test_file),
            processing_time=2.5,
            model_version="llama2",
            detected_language="en",
            chunked=False,
            chunk_count=None,
            user_config=user_config,
            effective_config=effective_config,
        )

        assert "processing_timestamp" in result
        assert result["model_version"] == "llama2"
        assert result["configuration"]["user_provided"] == user_config
        assert result["source"]["file_path"] == str(test_file)

    def test_timestamp_is_iso8601(self):
        """Test timestamp is ISO 8601 format with timezone."""
        result = extract_text_metadata(
            text="test",
            file_path=None,
            processing_time=1.0,
            model_version="test",
            detected_language=None,
            chunked=False,
            chunk_count=None,
            user_config={},
            effective_config={},
        )

        timestamp = result["processing_timestamp"]
        dt = datetime.fromisoformat(timestamp)
        assert dt.tzinfo == UTC


class TestTextSourceMetadata:
    """Tests for text source metadata extraction."""

    def test_extract_text_source_metadata_with_file(self, tmp_path):
        """Test text source metadata with file path."""
        test_file = tmp_path / "document.txt"
        test_content = "Test document with multiple words here."
        test_file.write_text(test_content)

        result = _extract_text_source_metadata(test_content, str(test_file), "en", False, None)

        assert result["file_path"] == str(test_file)
        assert isinstance(result["file_size_bytes"], int)
        assert result["input_length_words"] == 6
        assert result["input_length_chars"] == len(test_content)
        assert result["detected_language"] == "en"
        assert result["chunked"] is False
        assert result["chunk_count"] is None

    def test_extract_text_source_metadata_stdin(self):
        """Test text source metadata with stdin input."""
        text = "Input from stdin with some words."

        result = _extract_text_source_metadata(text, None, "en", False, None)

        assert result["file_path"] == "unavailable"
        assert result["file_size_bytes"] == "unavailable"
        assert result["input_length_words"] == 6
        assert result["input_length_chars"] == len(text)

    def test_extract_text_source_metadata_chunked(self):
        """Test text source metadata with chunking."""
        text = "Long text that was chunked into multiple pieces."

        result = _extract_text_source_metadata(text, None, "en", True, 3)

        assert result["chunked"] is True
        assert result["chunk_count"] == 3

    def test_extract_text_source_metadata_no_language(self):
        """Test text source metadata without language detection."""
        text = "Text without language detection."

        result = _extract_text_source_metadata(text, None, None, False, None)

        assert result["detected_language"] == "unavailable"

    def test_word_count_accuracy(self):
        """Test word count calculation accuracy."""
        text = "One two three four five"
        result = _extract_text_source_metadata(text, None, None, False, None)
        assert result["input_length_words"] == 5

        text_with_newlines = "One two\nthree four\nfive"
        result = _extract_text_source_metadata(text_with_newlines, None, None, False, None)
        assert result["input_length_words"] == 5

    def test_char_count_accuracy(self):
        """Test character count calculation accuracy."""
        text = "Test"
        result = _extract_text_source_metadata(text, None, None, False, None)
        assert result["input_length_chars"] == 4

        text_with_unicode = "Tëst"
        result = _extract_text_source_metadata(text_with_unicode, None, None, False, None)
        assert result["input_length_chars"] == 4

    def test_empty_text(self):
        """Test metadata extraction with empty text."""
        result = _extract_text_source_metadata("", None, None, False, None)

        assert result["input_length_words"] == 0
        assert result["input_length_chars"] == 0

    def test_file_size_unavailable_on_error(self, tmp_path):
        """Test file size is unavailable when file cannot be read."""
        result = _extract_text_source_metadata("text", "/nonexistent/file.txt", None, False, None)

        assert result["file_size_bytes"] == "unavailable"


class TestMetadataStructure:
    """Tests for metadata structure consistency."""

    def test_metadata_has_required_fields(self):
        """Test metadata contains all required fields."""
        result = extract_text_metadata(
            text="test",
            file_path=None,
            processing_time=1.0,
            model_version="model",
            detected_language=None,
            chunked=False,
            chunk_count=None,
            user_config={},
            effective_config={},
        )

        assert "processing_timestamp" in result
        assert "model_version" in result
        assert "configuration" in result
        assert "source" in result

    def test_configuration_structure(self):
        """Test configuration metadata structure."""
        user_config = {"model": "test"}
        effective_config = {"model": "test", "provider": "ollama"}

        result = extract_text_metadata(
            text="test",
            file_path=None,
            processing_time=1.0,
            model_version="model",
            detected_language=None,
            chunked=False,
            chunk_count=None,
            user_config=user_config,
            effective_config=effective_config,
        )

        assert result["configuration"]["user_provided"] == user_config
        assert result["configuration"]["effective"] == effective_config

    def test_source_metadata_has_required_fields(self):
        """Test source metadata contains all required fields."""
        result = extract_text_metadata(
            text="test",
            file_path=None,
            processing_time=1.0,
            model_version="model",
            detected_language=None,
            chunked=False,
            chunk_count=None,
            user_config={},
            effective_config={},
        )

        source = result["source"]
        required_fields = [
            "file_path",
            "file_size_bytes",
            "input_length_words",
            "input_length_chars",
            "detected_language",
            "chunked",
            "chunk_count",
        ]
        for field in required_fields:
            assert field in source
