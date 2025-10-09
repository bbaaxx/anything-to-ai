"""VLM model protocol implementation with MLX integration."""

import time
from typing import Any, Protocol
from abc import ABC, abstractmethod

from .vlm_exceptions import VLMProcessingError


class VLMModelProtocol(Protocol):
    """Protocol for VLM model implementations."""

    def process_image(self, image_path: str, prompt: str) -> dict[str, Any]:
        """Process image with VLM model."""
        ...

    def get_model_info(self) -> dict[str, str]:
        """Get model information."""
        ...

    def cleanup(self) -> None:
        """Clean up model resources."""
        ...


class BaseVLMModel(ABC):
    """Base class for VLM model implementations."""

    def __init__(self, model_name: str, model_version: str = "v1.0"):
        self.model_name = model_name
        self.model_version = model_version
        self._model_instance = None

    @abstractmethod
    def _load_model(self) -> Any:
        """Load the actual model instance."""

    @abstractmethod
    def _process_image_internal(self, image_path: str, prompt: str) -> str:
        """Internal image processing implementation."""

    def _ensure_model_loaded(self):
        """Ensure model is loaded (for pre-loading without timeout)."""
        if self._model_instance is None:
            self._model_instance = self._load_model()

    def process_image(self, image_path: str, prompt: str) -> dict[str, Any]:
        """
        Process image with VLM model.

        Args:
            image_path: Path to image file
            prompt: Text prompt for VLM processing

        Returns:
            Dict containing description, confidence, processing_time

        Raises:
            VLMProcessingError: If processing fails
            VLMTimeoutError: If processing times out
        """
        # Model should already be loaded by _ensure_model_loaded
        if self._model_instance is None:
            self._model_instance = self._load_model()

        start_time = time.time()

        try:
            description = self._process_image_internal(image_path, prompt)
            processing_time = time.time() - start_time

            return {
                "description": description,
                "confidence_score": None,  # Model-dependent
                "processing_time": processing_time,
                "model_info": self.get_model_info(),
            }

        except Exception as e:
            processing_time = time.time() - start_time
            msg = f"VLM processing failed: {e!s}"
            raise VLMProcessingError(msg, image_path=image_path, model_name=self.model_name, error_details=str(e))

    def get_model_info(self) -> dict[str, str]:
        """Get model information."""
        return {"name": self.model_name, "version": self.model_version}

    def cleanup(self) -> None:
        """Clean up model resources."""
        if self._model_instance is not None:
            # Model-specific cleanup
            self._model_instance = None


class MLXVLMModel(BaseVLMModel):
    """MLX-based VLM model implementation."""

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.capabilities = {"vision": True, "text": True}

    def _load_model(self) -> Any:
        """Load MLX VLM model."""
        try:
            import mlx_vlm

            # mlx_vlm.load returns a tuple of (model, processor)
            model, processor = mlx_vlm.load(self.model_name)
            return {"model": model, "processor": processor}

        except Exception as e:
            from .vlm_exceptions import VLMModelLoadError

            msg = f"Failed to load MLX model '{self.model_name}'"
            raise VLMModelLoadError(msg, model_name=self.model_name, error_reason=str(e))

    def _process_image_internal(self, image_path: str, prompt: str) -> str:
        """Process image using MLX VLM."""
        try:
            import mlx_vlm

            # Extract model and processor from loaded instance
            model = self._model_instance["model"]
            processor = self._model_instance["processor"]

            # Generate description using MLX VLM
            # Gemma-3 requires explicit image token in the prompt
            formatted_prompt = f"<start_of_image>{prompt}"

            result = mlx_vlm.generate(model=model, processor=processor, prompt=formatted_prompt, image=image_path, max_tokens=100, temperature=0.0)

            # Extract text from result
            if hasattr(result, "text"):
                return result.text
            if isinstance(result, str):
                return result
            return str(result)

        except Exception as e:
            # Fallback to descriptive error handling
            import os

            filename = os.path.basename(image_path)
            msg = f"Failed to process image {filename} with MLX VLM: {e!s}"
            raise VLMProcessingError(msg, image_path=image_path, model_name=self.model_name, error_details=str(e))


class MockVLMModel(BaseVLMModel):
    """Mock VLM model for testing purposes."""

    def __init__(self, model_name: str = "mock/test-model", **kwargs):
        super().__init__(model_name, **kwargs)

    def _load_model(self) -> Any:
        """Load mock model."""
        return "mock_model_instance"

    def _process_image_internal(self, image_path: str, prompt: str) -> str:
        """Mock image processing."""
        import os

        filename = os.path.basename(image_path)
        return f"Mock VLM description for {filename}"


def create_vlm_model(model_name: str, **kwargs) -> VLMModelProtocol:
    """
    Factory function to create appropriate VLM model instance.

    Args:
        model_name: Name of the VLM model
        **kwargs: Additional model configuration

    Returns:
        VLMModelProtocol: VLM model instance
    """
    if model_name.startswith("mock/") or model_name == "test":
        return MockVLMModel(model_name, **kwargs)
    # Default to MLX implementation for real models
    return MLXVLMModel(model_name, **kwargs)
