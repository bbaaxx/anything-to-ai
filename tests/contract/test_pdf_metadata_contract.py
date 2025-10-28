"""Contract tests for PDF extractor metadata structure."""

import pytest


class TestPDFExtractionResultMetadata:
    """Test ExtractionResult metadata field contract."""

    def test_extraction_result_has_metadata_field(self):
        from anyfile_to_ai.pdf_extractor.models import ExtractionResult

        result = ExtractionResult(success=True, pages=[], total_pages=0, total_chars=0, processing_time=0.1)
        assert hasattr(result, "metadata"), "ExtractionResult must have metadata field"

    def test_metadata_is_optional_dict_or_none(self):
        from anyfile_to_ai.pdf_extractor.models import ExtractionResult

        result_without = ExtractionResult(success=True, pages=[], total_pages=0, total_chars=0, processing_time=0.1)
        assert result_without.metadata is None

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:30:00+00:00",
                "model_version": "pdfplumber-0.11.7",
                "processing_time_seconds": 0.1,
            },
            "configuration": {"user_provided": {}, "effective": {}},
            "source": {
                "file_path": "test.pdf",
                "file_size_bytes": 1000,
                "page_count": 1,
                "creation_date": "unavailable",
            },
        }
        result_with = ExtractionResult(
            success=True,
            pages=[],
            total_pages=0,
            total_chars=0,
            processing_time=0.1,
            metadata=metadata,
        )
        assert result_with.metadata == metadata

    def test_metadata_structure_matches_schema(self):
        from anyfile_to_ai.pdf_extractor.models import ExtractionResult

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:30:00+00:00",
                "model_version": "pdfplumber-0.11.7",
                "processing_time_seconds": 2.5,
            },
            "configuration": {
                "user_provided": {"format": "json"},
                "effective": {"format": "json", "stream": False, "progress": True},
            },
            "source": {
                "file_path": "/path/to/document.pdf",
                "file_size_bytes": 1234567,
                "page_count": 10,
                "creation_date": "2025-01-15T09:30:00+00:00",
                "modification_date": "unavailable",
                "author": "Test Author",
                "title": "Test Document",
            },
        }

        result = ExtractionResult(
            success=True,
            pages=[],
            total_pages=0,
            total_chars=0,
            processing_time=2.5,
            metadata=metadata,
        )

        assert "processing" in result.metadata
        assert "configuration" in result.metadata
        assert "source" in result.metadata

        assert result.metadata["processing"]["timestamp"]
        assert result.metadata["processing"]["model_version"]
        assert result.metadata["processing"]["processing_time_seconds"] == 2.5

        assert "user_provided" in result.metadata["configuration"]
        assert "effective" in result.metadata["configuration"]

        assert result.metadata["source"]["file_path"] == "/path/to/document.pdf"
        assert result.metadata["source"]["page_count"] == 10
        assert result.metadata["source"]["file_size_bytes"] == 1234567
