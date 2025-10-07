"""MLX adapter for LLM client.

This adapter wraps the existing image_processor VLM functionality to provide
OpenAI-compatible chat completion interface for MLX-powered vision models.
"""

import os
import re
import time
import uuid
from pathlib import Path

from anyfile_to_ai.llm_client.adapters.base import BaseAdapter
from anyfile_to_ai.llm_client.exceptions import (
    ConfigurationError,
    ConnectionError,
    GenerationError,
    ModelNotFoundError,
)
from anyfile_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo


class MLXAdapter(BaseAdapter):
    """Adapter for MLX Vision Language Models via image_processor."""

    def __init__(self, config):
        """Initialize MLX adapter.

        Args:
            config: LLMConfig instance

        Raises:
            ConfigurationError: If VISION_MODEL environment variable is not set
        """
        super().__init__(config)

        # Check for VISION_MODEL environment variable
        self.vision_model = os.environ.get("VISION_MODEL")
        if not self.vision_model:
            raise ConfigurationError(
                "VISION_MODEL environment variable must be set for MLX adapter",
                provider="mlx",
            )

    def _extract_image_path(self, content: str) -> str | None:
        """Extract image file path from message content.

        Supports patterns like:
        - "Describe the image at path/to/image.jpg"
        - "What's in path/to/image.png"
        - Just "path/to/image.jpg"

        Args:
            content: Message content that may contain image path

        Returns:
            Extracted image path or None if not found
        """
        # Try to find file path patterns
        # Look for common image extensions
        path_pattern = r"([^\s]+\.(?:jpg|jpeg|png|gif|bmp|webp))"
        match = re.search(path_pattern, content, re.IGNORECASE)

        if match:
            path = match.group(1)
            # Clean up common trailing characters
            path = path.rstrip(".,;:!?")
            return path

        return None

    def _get_image_path_from_request(self, request: LLMRequest) -> str:
        """Extract and validate image path from request messages."""
        image_path = None
        for message in request.messages:
            if message.role == "user":
                image_path = self._extract_image_path(message.content)
                if image_path:
                    break

        if not image_path:
            raise ConfigurationError(
                "No image path found in message content. Include image path in format: 'Describe path/to/image.jpg'",
                provider="mlx",
            )

        if not Path(image_path).exists():
            raise GenerationError(f"Image file not found: {image_path}", provider="mlx")

        return image_path

    def _process_with_image_processor(self, image_path: str, request: LLMRequest, image_processor):
        """Process image using image_processor module."""
        # Determine description style from temperature
        style = "detailed"
        if request.temperature < 0.3:
            style = "brief"
        elif request.temperature > 1.0:
            style = "technical"

        config = image_processor.create_config(
            description_style=style,
            max_length=request.max_tokens or 500,
        )

        return image_processor.process_image(image_path, config)

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using MLX vision model.

        The adapter translates OpenAI chat format to MLX image processing:
        - Extracts image path from user message content
        - Processes image using existing image_processor
        - Returns result in OpenAI response format

        Args:
            request: LLM request with messages

        Returns:
            LLM response with image description

        Raises:
            GenerationError: If image processing fails
            ConfigurationError: If no image path found in messages
        """
        try:
            from anyfile_to_ai import image_processor
        except ImportError as e:
            raise ConnectionError("image_processor module not available", provider="mlx", original_error=e)

        image_path = self._get_image_path_from_request(request)
        start_time = time.time()

        try:
            result = self._process_with_image_processor(image_path, request, image_processor)
            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                content=result.description,
                model=self.vision_model,
                finish_reason="stop",
                response_id=str(uuid.uuid4()),
                provider="mlx",
                latency_ms=latency_ms,
                usage=None,  # MLX doesn't provide token usage
            )

        except image_processor.ImageNotFoundError as e:
            raise GenerationError(f"Image not found: {image_path}", provider="mlx", original_error=e)
        except image_processor.VLMConfigurationError as e:
            raise ConfigurationError(f"VLM configuration error: {e}", provider="mlx", original_error=e)
        except image_processor.VLMModelNotFoundError as e:
            raise ModelNotFoundError(
                f"VLM model not found: {self.vision_model}",
                provider="mlx",
                original_error=e,
            )
        except image_processor.VLMProcessingError as e:
            raise GenerationError(f"VLM processing error: {e}", provider="mlx", original_error=e)
        except Exception as e:
            raise GenerationError(
                f"Unexpected error during image processing: {e}",
                provider="mlx",
                original_error=e,
            )

    def list_models(self) -> list[ModelInfo]:
        """List available MLX vision models.

        Returns:
            List containing the configured VISION_MODEL

        Raises:
            ConnectionError: If image_processor module is not available
        """
        import importlib.util

        if importlib.util.find_spec("image_processor") is None:
            raise ConnectionError("image_processor module not available", provider="mlx")

        # Return the currently configured model
        return [
            ModelInfo(
                id=self.vision_model,
                provider="mlx",
                object="model",
                description="MLX Vision Language Model",
            ),
        ]

    def health_check(self) -> bool:
        """Check if MLX adapter is operational.

        Returns:
            True if image_processor is available and model is configured
        """
        try:
            # Check if VISION_MODEL is set
            if not self.vision_model:
                return False

            # Try to validate model availability
            from anyfile_to_ai import image_processor

            return image_processor.validate_model_availability(self.vision_model)
        except Exception:
            return False
