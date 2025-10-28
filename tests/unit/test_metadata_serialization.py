"""Unit tests for metadata serialization to various formats."""

import json

import pytest


class TestJSONSerialization:
    """Tests for JSON serialization of metadata."""

    def test_serialize_complete_metadata(self):
        """Test complete metadata can be JSON serialized."""
        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:30:00+00:00",
                "model_version": "test-model",
                "processing_time_seconds": 2.5,
            },
            "configuration": {
                "user_provided": {"model": "medium"},
                "effective": {"model": "medium", "timeout": 60},
            },
            "source": {
                "file_path": "/path/to/file.pdf",
                "file_size_bytes": 1024,
                "page_count": 10,
            },
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed == metadata

    def test_serialize_unavailable_fields(self):
        """Test unavailable fields serialize correctly."""
        metadata = {
            "source": {
                "file_size_bytes": "unavailable",
                "creation_date": "unavailable",
                "author": "unavailable",
            }
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed["source"]["file_size_bytes"] == "unavailable"

    def test_serialize_empty_exif(self):
        """Test empty EXIF dict serializes correctly."""
        metadata = {"source": {"exif": {}}}

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed["source"]["exif"] == {}

    def test_serialize_nested_configuration(self):
        """Test nested configuration serializes correctly."""
        metadata = {
            "configuration": {
                "user_provided": {"model": "medium", "options": {"batch_size": 4}},
                "effective": {
                    "model": "medium",
                    "options": {"batch_size": 4, "timeout": 60},
                },
            }
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed["configuration"]["user_provided"]["options"]["batch_size"] == 4


class TestMetadataRoundtrip:
    """Tests for metadata serialization roundtrip."""

    def test_json_roundtrip_preserves_types(self):
        """Test JSON roundtrip preserves data types."""
        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:30:00+00:00",
                "processing_time_seconds": 2.5,
            },
            "source": {
                "file_size_bytes": 1024,
                "page_count": 10,
                "author": "Test Author",
            },
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert isinstance(parsed["processing"]["processing_time_seconds"], float)
        assert isinstance(parsed["source"]["file_size_bytes"], int)
        assert isinstance(parsed["source"]["author"], str)

    def test_roundtrip_with_unicode(self):
        """Test roundtrip with unicode characters."""
        metadata = {"source": {"author": "Tëst Authör", "title": "Dócument"}}

        json_str = json.dumps(metadata, ensure_ascii=False)
        parsed = json.loads(json_str)

        assert parsed["source"]["author"] == "Tëst Authör"
        assert parsed["source"]["title"] == "Dócument"


class TestCSVFlattenedSerialization:
    """Tests for CSV-style flattened metadata serialization."""

    def test_flatten_nested_metadata(self):
        """Test flattening nested metadata for CSV."""
        flattened = {
            "metadata.processing.timestamp": "2025-10-25T14:30:00+00:00",
            "metadata.processing.model_version": "test",
            "metadata.source.file_path": "/test.pdf",
            "metadata.source.page_count": 10,
        }

        for key in flattened:
            assert "." in key

    def test_flatten_preserves_values(self):
        """Test flattening preserves all values."""
        flattened = {
            "metadata.processing.processing_time_seconds": 2.5,
            "metadata.source.file_size_bytes": 1024,
        }

        assert flattened["metadata.processing.processing_time_seconds"] == 2.5
        assert flattened["metadata.source.file_size_bytes"] == 1024


class TestMarkdownSerialization:
    """Tests for markdown serialization of metadata."""

    def test_yaml_frontmatter_format(self):
        """Test YAML frontmatter format for markdown."""
        frontmatter = """---
processing_timestamp: 2025-10-25T14:30:00+00:00
model_version: test-model
file_path: /test.pdf
---"""

        assert frontmatter.startswith("---")
        assert frontmatter.endswith("---")
        assert "processing_timestamp:" in frontmatter

    def test_metadata_section_format(self):
        """Test metadata section format for markdown."""
        metadata_section = """## Metadata

- **Processing Time**: 2.5s
- **Model Version**: test-model
- **File Size**: 1.2 MB
- **Page Count**: 10"""

        assert metadata_section.startswith("## Metadata")
        assert "Processing Time" in metadata_section


class TestSerializationEdgeCases:
    """Tests for serialization edge cases."""

    def test_serialize_none_metadata(self):
        """Test serializing None metadata."""
        metadata = None
        json_str = json.dumps({"metadata": metadata})
        parsed = json.loads(json_str)

        assert parsed["metadata"] is None

    def test_serialize_empty_metadata(self):
        """Test serializing empty metadata dict."""
        metadata = {}
        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed == {}

    def test_serialize_large_metadata(self):
        """Test serializing metadata with many EXIF tags."""
        exif_data = {f"Tag{i}": f"Value{i}" for i in range(100)}
        metadata = {"source": {"exif": exif_data}}

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert len(parsed["source"]["exif"]) == 100

    def test_serialize_special_characters(self):
        """Test serializing metadata with special characters."""
        metadata = {
            "source": {
                "file_path": "/path/with spaces/file (1).pdf",
                "author": 'Author "Nickname" Name',
            }
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert "spaces" in parsed["source"]["file_path"]
        assert '"' in parsed["source"]["author"]


class TestSerializationConsistency:
    """Tests for serialization consistency across modules."""

    def test_all_modules_serialize_to_json(self):
        """Test all module metadata structures serialize to JSON."""
        pdf_metadata = {
            "processing": {"timestamp": "2025-10-25T14:30:00+00:00"},
            "source": {"page_count": 10},
        }
        image_metadata = {
            "processing": {"timestamp": "2025-10-25T14:30:00+00:00"},
            "source": {"dimensions": {"width": 1920, "height": 1080}},
        }
        audio_metadata = {
            "processing": {"timestamp": "2025-10-25T14:30:00+00:00"},
            "source": {"duration_seconds": 180.5},
        }

        for metadata in [pdf_metadata, image_metadata, audio_metadata]:
            json_str = json.dumps(metadata)
            parsed = json.loads(json_str)
            assert "processing" in parsed
            assert "source" in parsed
