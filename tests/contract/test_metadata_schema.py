import json
from pathlib import Path

import pytest


class TestMetadataSchemaValidation:
    @pytest.fixture
    def schema_path(self):
        return Path(__file__).parent.parent.parent / "specs" / "015-extend-all-result" / "contracts" / "metadata-schema.json"

    @pytest.fixture
    def metadata_schema(self, schema_path):
        with open(schema_path) as f:
            return json.load(f)

    def test_schema_file_exists(self, schema_path):
        assert schema_path.exists(), f"Metadata schema not found at {schema_path}"

    def test_schema_has_required_sections(self, metadata_schema):
        assert "properties" in metadata_schema
        assert "processing" in metadata_schema["properties"]
        assert "configuration" in metadata_schema["properties"]
        assert "source" in metadata_schema["properties"]

    def test_processing_metadata_structure(self, metadata_schema):
        processing = metadata_schema["properties"]["processing"]
        assert processing["type"] == "object"
        assert "timestamp" in processing["properties"]
        assert "model_version" in processing["properties"]
        assert "processing_time_seconds" in processing["properties"]

    def test_configuration_metadata_structure(self, metadata_schema):
        configuration = metadata_schema["properties"]["configuration"]
        assert configuration["type"] == "object"
        assert "user_provided" in configuration["properties"]
        assert "effective" in configuration["properties"]

    def test_source_metadata_has_type_specific_schemas(self, metadata_schema):
        source = metadata_schema["properties"]["source"]
        assert "oneOf" in source
        assert len(source["oneOf"]) == 4

    def test_pdf_source_metadata_fields(self, metadata_schema):
        pdf_schema = metadata_schema["$defs"]["PDFSourceMetadata"]
        required_fields = ["file_path", "file_size_bytes", "page_count", "creation_date"]
        for field in required_fields:
            assert field in pdf_schema["properties"], f"PDF schema missing required field: {field}"

    def test_image_source_metadata_fields(self, metadata_schema):
        image_schema = metadata_schema["$defs"]["ImageSourceMetadata"]
        required_fields = ["file_path", "file_size_bytes", "dimensions", "format", "exif"]
        for field in required_fields:
            assert field in image_schema["properties"], f"Image schema missing required field: {field}"

    def test_audio_source_metadata_fields(self, metadata_schema):
        audio_schema = metadata_schema["$defs"]["AudioSourceMetadata"]
        required_fields = ["file_path", "file_size_bytes", "duration_seconds", "sample_rate_hz", "channels", "format", "detected_language", "language_confidence"]
        for field in required_fields:
            assert field in audio_schema["properties"], f"Audio schema missing required field: {field}"

    def test_text_source_metadata_fields(self, metadata_schema):
        text_schema = metadata_schema["$defs"]["TextSourceMetadata"]
        required_fields = ["file_path", "file_size_bytes", "input_length_words", "input_length_chars", "detected_language", "chunked"]
        for field in required_fields:
            assert field in text_schema["properties"], f"Text schema missing required field: {field}"

    def test_timestamp_format_is_date_time(self, metadata_schema):
        timestamp = metadata_schema["properties"]["processing"]["properties"]["timestamp"]
        assert timestamp["format"] == "date-time"

    def test_unavailable_string_allowed_for_optional_fields(self, metadata_schema):
        file_size = metadata_schema["$defs"]["PDFSourceMetadata"]["properties"]["file_size_bytes"]
        assert "oneOf" in file_size
        has_unavailable = any(item.get("const") == "unavailable" for item in file_size["oneOf"])
        assert has_unavailable, "file_size_bytes should allow 'unavailable' as a const value"


class TestMetadataDisabledByDefault:
    def test_pdf_extraction_result_metadata_none_without_flag(self):
        from anyfile_to_ai.pdf_extractor.models import ExtractionResult

        result = ExtractionResult(success=True, pages=[], total_pages=0, total_chars=0, processing_time=0.1)
        assert hasattr(result, "metadata"), "ExtractionResult must have metadata field"
        assert result.metadata is None, "metadata should be None when not provided"

    def test_image_description_result_metadata_none_without_flag(self):
        from anyfile_to_ai.image_processor.models import DescriptionResult

        result = DescriptionResult(
            image_path="test.jpg",
            description="test",
            confidence_score=None,
            processing_time=0.0,
            model_used="test",
            prompt_used="test",
            success=True,
        )
        assert hasattr(result, "metadata"), "DescriptionResult must have metadata field"
        assert result.metadata is None, "metadata should be None when not provided"

    def test_audio_transcription_result_metadata_none_without_flag(self):
        from anyfile_to_ai.audio_processor.models import TranscriptionResult

        result = TranscriptionResult(
            audio_path="test.mp3",
            text="test",
            confidence_score=None,
            processing_time=0.0,
            model_used="test",
            quantization="none",
            detected_language=None,
            success=True,
            error_message=None,
        )
        assert hasattr(result, "metadata"), "TranscriptionResult must have metadata field"
        assert result.metadata is None, "metadata should be None when not provided"

    def test_text_summary_metadata_can_be_none(self):
        from anyfile_to_ai.text_summarizer.models import SummaryResult

        result = SummaryResult(summary="test summary", tags=["test1", "test2", "test3"], metadata=None)
        assert result.metadata is None, "SummaryResult.metadata should support None"
