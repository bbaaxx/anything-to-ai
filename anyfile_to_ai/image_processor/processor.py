"""Core VLM processing functionality."""

import os
import time
from typing import Any, Dict
from PIL import Image
from .models import ImageDocument, DescriptionResult, ProcessingConfig
from .exceptions import (
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError,
    ModelLoadError,
    ProcessingError,
    ProcessingTimeoutError,
)
from .vlm_exceptions import VLMConfigurationError, VLMModelLoadError, VLMProcessingError
from .vlm_config import load_vlm_configuration, merge_processing_config_with_vlm
from .vlm_processor import get_global_vlm_processor
from .model_loader import get_global_model_loader

# Supported image formats
SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "GIF", "BMP", "WEBP"}


class VLMProcessor:
    """Core processor for VLM image description generation."""

    def __init__(self):
        self._vlm_processor = get_global_vlm_processor()
        self._model_loader = get_global_model_loader()
        self._current_config = None

    def load_model(self, model_name: str) -> None:
        """Load MLX-VLM model for processing."""
        try:
            # Use the VLM configuration system
            vlm_config = load_vlm_configuration()
            self._current_config = vlm_config

            # Validate and load model through model loader
            self._model_loader.validate_and_load_model(vlm_config)

        except (VLMConfigurationError, VLMModelLoadError) as e:
            raise ModelLoadError(model_name, str(e))
        except Exception as e:
            raise ModelLoadError(model_name, f"Unexpected error: {str(e)}")

    def validate_image(self, file_path: str) -> ImageDocument:
        """Validate image file and extract metadata."""
        if not os.path.exists(file_path):
            raise ImageNotFoundError(file_path)

        try:
            with Image.open(file_path) as img:
                # Extract image metadata
                format_name = img.format or os.path.splitext(file_path)[1][1:].upper()

                if format_name not in SUPPORTED_FORMATS:
                    raise UnsupportedFormatError(file_path, format_name)

                width, height = img.size
                file_size = os.path.getsize(file_path)

                # Determine if large image (>10MB or >2048px in any dimension)
                is_large = file_size > 10 * 1024 * 1024 or width > 2048 or height > 2048

                return ImageDocument(
                    file_path=file_path,
                    format=format_name,
                    width=width,
                    height=height,
                    file_size=file_size,
                    is_large_image=is_large,
                )

        except (IOError, OSError) as e:
            raise CorruptedImageError(file_path, str(e))

    def preprocess_image(self, image_document: ImageDocument) -> Any:
        """Preprocess image for VLM processing."""
        try:
            with Image.open(image_document.file_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize if too large (for performance)
                max_size = (1024, 1024)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                return img
        except Exception as e:
            raise ProcessingError(
                image_document.file_path, f"Preprocessing failed: {e}"
            )

    def process_single_image(
        self, image_document: ImageDocument, config: ProcessingConfig
    ) -> DescriptionResult:
        """Process single image with VLM."""
        start_time = time.time()

        try:
            # Ensure VLM configuration is loaded
            if self._current_config is None:
                self.load_model(config.model_name)

            # Merge VLM configuration with processing config
            vlm_config = self._current_config
            merge_processing_config_with_vlm(config, vlm_config)

            # Preprocess image
            self.preprocess_image(image_document)

            # Generate prompt
            prompt = config.prompt_template.format(style=config.description_style)

            # Process with real VLM
            vlm_result = self._vlm_processor.process_image_with_vlm(
                image_document.file_path,
                prompt,
                vlm_config
            )

            # Create technical metadata
            technical_metadata = self._create_technical_metadata(image_document)

            processing_time = time.time() - start_time

            # Check timeout
            if processing_time > config.timeout_seconds:
                raise ProcessingTimeoutError(
                    image_document.file_path, config.timeout_seconds
                )

            return DescriptionResult(
                image_path=image_document.file_path,
                description=vlm_result["description"],
                confidence_score=vlm_result.get("confidence_score"),
                processing_time=processing_time,
                model_used=vlm_result["model_info"]["name"],
                prompt_used=prompt,
                success=True,
                # Enhanced VLM fields
                technical_metadata=technical_metadata,
                vlm_processing_time=vlm_result["processing_time"],
                model_version=vlm_result["model_info"]["version"]
            )

        except (VLMProcessingError, VLMConfigurationError) as e:
            processing_time = time.time() - start_time
            raise ProcessingError(image_document.file_path, str(e))
        except Exception as e:
            processing_time = time.time() - start_time
            if isinstance(e, (ProcessingTimeoutError, ProcessingError)):
                raise
            else:
                raise ProcessingError(image_document.file_path, str(e))

    def _create_technical_metadata(self, image_doc: ImageDocument) -> Dict[str, Any]:
        """Create technical metadata from image document."""
        return {
            "format": image_doc.format,
            "dimensions": [image_doc.width, image_doc.height],
            "file_size": image_doc.file_size,
            "is_large_image": image_doc.is_large_image
        }

    def process_with_vlm(self, image_path: str, config: ProcessingConfig) -> DescriptionResult:
        """Public method to process image with VLM (for backward compatibility)."""
        image_doc = self.validate_image(image_path)
        return self.process_single_image(image_doc, config)

    def cleanup(self) -> None:
        """Clean up model resources."""
        if self._vlm_processor:
            self._vlm_processor.cleanup()
        self._current_config = None
