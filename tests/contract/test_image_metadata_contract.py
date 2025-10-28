"""Contract tests for Image processor metadata structure."""

import pytest


class TestDescriptionResultMetadata:
    """Test DescriptionResult metadata field contract."""

    def test_description_result_has_metadata_field(self):
        from anyfile_to_ai.image_processor.models import DescriptionResult

        result = DescriptionResult(
            image_path="test.jpg",
            description="test",
            confidence_score=None,
            processing_time=1.0,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
        )
        assert hasattr(result, "metadata"), "DescriptionResult must have metadata field"

    def test_metadata_is_optional_dict_or_none(self):
        from anyfile_to_ai.image_processor.models import DescriptionResult

        result_without = DescriptionResult(
            image_path="test.jpg",
            description="test",
            confidence_score=None,
            processing_time=1.0,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
        )
        assert result_without.metadata is None

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:35:00+00:00",
                "model_version": "mlx-community/gemma-3-4b",
                "processing_time_seconds": 1.8,
            },
            "configuration": {
                "user_provided": {"style": "detailed"},
                "effective": {
                    "style": "detailed",
                    "max_description_length": 500,
                    "timeout_seconds": 60,
                },
            },
            "source": {
                "file_path": "test.jpg",
                "file_size_bytes": 2048576,
                "dimensions": {"width": 1920, "height": 1080},
                "format": "JPEG",
                "exif": {},
            },
        }
        result_with = DescriptionResult(
            image_path="test.jpg",
            description="test",
            confidence_score=None,
            processing_time=1.0,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
            metadata=metadata,
        )
        assert result_with.metadata == metadata

    def test_metadata_includes_exif_data(self):
        from anyfile_to_ai.image_processor.models import DescriptionResult

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:35:00+00:00",
                "model_version": "mlx-community/gemma-3-4b",
                "processing_time_seconds": 1.8,
            },
            "configuration": {"user_provided": {}, "effective": {}},
            "source": {
                "file_path": "photo.jpg",
                "file_size_bytes": 2048576,
                "dimensions": {"width": 1920, "height": 1080},
                "format": "JPEG",
                "exif": {
                    "Make": "Canon",
                    "Model": "EOS 5D Mark IV",
                    "FNumber": 2.8,
                    "ISOSpeedRatings": 400,
                },
                "camera_info": {"make": "Canon", "model": "EOS 5D Mark IV"},
            },
        }

        result = DescriptionResult(
            image_path="photo.jpg",
            description="A sunset photo",
            confidence_score=None,
            processing_time=1.8,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
            metadata=metadata,
        )

        assert "exif" in result.metadata["source"]
        assert result.metadata["source"]["exif"]["Make"] == "Canon"
        assert result.metadata["source"]["dimensions"]["width"] == 1920


class TestProcessingResultMetadataPerImage:
    """Test that batch processing includes per-image metadata."""

    def test_batch_result_contains_per_image_metadata(self):
        from anyfile_to_ai.image_processor.models import DescriptionResult, ProcessingResult

        metadata1 = {
            "processing": {"timestamp": "2025-10-25T14:35:00+00:00", "model_version": "test", "processing_time_seconds": 1.0},
            "configuration": {"user_provided": {}, "effective": {}},
            "source": {"file_path": "img1.jpg", "file_size_bytes": 1000, "dimensions": {"width": 100, "height": 100}, "format": "JPEG", "exif": {}},
        }

        result1 = DescriptionResult(
            image_path="img1.jpg",
            description="test1",
            confidence_score=None,
            processing_time=1.0,
            model_used="test",
            prompt_used="test",
            success=True,
            metadata=metadata1,
        )

        batch_result = ProcessingResult(
            success=True,
            results=[result1],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.0,
        )

        assert len(batch_result.results) == 1
        assert batch_result.results[0].metadata is not None
        assert batch_result.results[0].metadata["source"]["file_path"] == "img1.jpg"
