"""Core VLM processing functionality."""

import os
import time
from typing import Any
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

# Supported image formats
SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "GIF", "BMP", "WEBP"}


class VLMProcessor:
    """Core processor for VLM image description generation."""

    def __init__(self):
        self._model = None
        self._model_name = None

    def load_model(self, model_name: str) -> None:
        """Load MLX-VLM model for processing."""
        try:
            # For now, simulate model loading
            # In real implementation, would load MLX-VLM model here
            self._model_name = model_name
            self._model = f"mock_model_{model_name}"
            time.sleep(0.1)  # Simulate loading time
        except Exception as e:
            raise ModelLoadError(model_name, str(e))

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
            # Ensure model is loaded
            if not self._model:
                self.load_model(config.model_name)

            # Preprocess image
            self.preprocess_image(image_document)

            # Simulate VLM processing time
            processing_delay = min(0.5, config.timeout_seconds / 2)
            time.sleep(processing_delay)

            # Generate mock description based on config
            prompt = config.prompt_template.format(style=config.description_style)
            description = self._generate_mock_description(
                image_document, config.description_style, config.max_description_length
            )

            processing_time = time.time() - start_time

            # Check timeout
            if processing_time > config.timeout_seconds:
                raise ProcessingTimeoutError(
                    image_document.file_path, config.timeout_seconds
                )

            return DescriptionResult(
                image_path=image_document.file_path,
                description=description,
                confidence_score=0.85,  # Mock confidence
                processing_time=processing_time,
                model_used=self._model_name,
                prompt_used=prompt,
                success=True,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            if isinstance(e, (ProcessingTimeoutError, ProcessingError)):
                raise
            else:
                raise ProcessingError(image_document.file_path, str(e))

    def _generate_mock_description(
        self, image_doc: ImageDocument, style: str, max_length: int
    ) -> str:
        """Generate mock description for testing purposes."""
        base_descriptions = {
            "detailed": f"This is a {image_doc.format.lower()} image with dimensions "
            f"{image_doc.width}x{image_doc.height} pixels. The image contains visual "
            f"content that would be processed by a Vision Language Model to generate "
            f"a comprehensive description of the scene, objects, colors, and elements.",
            "brief": f"A {image_doc.format.lower()} image ({image_doc.width}x{image_doc.height}) "
            f"containing visual content.",
            "technical": f"Image file: {image_doc.format} format, resolution "
            f"{image_doc.width}x{image_doc.height}, file size {image_doc.file_size} "
            f"bytes. Technical analysis would identify image properties and artifacts.",
        }

        description = base_descriptions.get(style, base_descriptions["detailed"])

        # Truncate to max length
        if len(description) > max_length:
            description = description[: max_length - 3] + "..."

        return description

    def cleanup(self) -> None:
        """Clean up model resources."""
        self._model = None
        self._model_name = None
