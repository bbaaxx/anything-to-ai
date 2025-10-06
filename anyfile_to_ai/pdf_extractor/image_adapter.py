"""Adapter for integrating image_processor module with PDF extraction."""

from typing import Optional, Any
from PIL import Image
import tempfile
import os

from .exceptions import VLMConfigurationError, VLMServiceError


class ImageProcessorAdapter:
    """Adapter to integrate image_processor module with PDF extraction."""

    def __init__(self):
        """Initialize the adapter."""
        self._image_processor = None
        self._config = None

    def _get_processor(self):
        """Get image processor instance."""
        if self._image_processor is None:
            try:
                import anyfile_to_ai.image_processor
                self._image_processor = image_processor
            except ImportError as e:
                raise VLMConfigurationError(
                    f"image_processor module not available: {e}",
                    config_key="image_processor"
                )
        return self._image_processor

    def _get_config(self, processing_config):
        """Get or create processing config."""
        if self._config is None or processing_config:
            try:
                processor = self._get_processor()
                if processing_config and hasattr(processing_config, 'description_style'):
                    # Use provided config
                    self._config = processing_config
                else:
                    # Create default config
                    self._config = processor.create_config(
                        description_style="detailed",
                        max_length=200,
                        batch_size=1
                    )
            except Exception as e:
                raise VLMConfigurationError(
                    f"Failed to create processing config: {e}",
                    config_key="ProcessingConfig"
                )
        return self._config

    def process_image(self, pil_image: Image.Image, processing_config=None) -> Any:
        """Process PIL image and return description result."""
        try:
            processor = self._get_processor()
            config = self._get_config(processing_config)

            # Save PIL image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                pil_image.save(temp_file.name, format='PNG')
                temp_path = temp_file.name

            try:
                # Process with image_processor
                result = processor.process_image(temp_path, config)
                return result
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        except Exception as e:
            raise VLMServiceError(f"Image processing failed: {e}")

    def validate_configuration(self) -> bool:
        """Validate that image processing is properly configured."""
        try:
            processor = self._get_processor()
            # Check if we can validate model availability
            if hasattr(processor, 'validate_model_availability'):
                return processor.validate_model_availability()
            return True
        except Exception:
            return False

    def get_model_name(self) -> Optional[str]:
        """Get the currently configured model name."""
        try:
            return os.getenv('VISION_MODEL')
        except Exception:
            return None
