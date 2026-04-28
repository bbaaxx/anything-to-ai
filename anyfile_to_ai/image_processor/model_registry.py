"""VLM model registry and loaded model management."""

from dataclasses import dataclass
from typing import Any
import time
import threading

from .vlm_exceptions import VLMModelLoadError, VLMModelNotFoundError
from .vlm_models import ModelConfiguration


@dataclass
class LoadedModel:
    """Represents an active VLM model instance in memory."""

    model_instance: Any
    model_name: str
    model_version: str
    memory_usage: int
    load_time: float
    capabilities: dict[str, Any]

    @property
    def is_ready(self) -> bool:
        """Check if model is ready for processing."""
        return self.model_instance is not None

    @property
    def model_info(self) -> dict[str, str]:
        """Get model information dictionary."""
        return {"name": self.model_name, "version": self.model_version}

    def cleanup(self) -> None:
        """Clean up model resources."""
        if self.model_instance is not None:
            # MLX models can be cleaned up by setting to None
            # The garbage collector will handle the rest
            self.model_instance = None


class VLMModelRegistry:
    """Registry for managing VLM models and their lifecycle."""

    def __init__(self):
        self.available_models: dict[str, dict[str, Any]] = {}
        self.loaded_model: LoadedModel | None = None
        self.validation_cache: dict[str, bool] = {}
        self._lock = threading.Lock()

    def validate_model(self, model_name: str) -> bool:
        """
        Validate that specified VLM model is available.

        Args:
            model_name: VLM model identifier

        Returns:
            bool: True if model name format is valid
        """
        # Check cache first
        if model_name in self.validation_cache:
            return self.validation_cache[model_name]

        try:
            # Basic validation - check if model name format is reasonable
            # Accept any valid HuggingFace-style model identifier (org/model-name)
            if not model_name or "/" not in model_name:
                self.validation_cache[model_name] = False
                return False

            # Accept any properly formatted model name
            # Actual availability will be checked at load time (may trigger download)
            self.validation_cache[model_name] = True
            return True

        except Exception:
            self.validation_cache[model_name] = False
            return False

    def load_model(self, config: ModelConfiguration) -> LoadedModel:
        """
        Load VLM model instance.

        Args:
            config: VLM configuration

        Returns:
            LoadedModel: Loaded model instance

        Raises:
            VLMModelLoadError: If model loading fails
            VLMModelNotFoundError: If model not found
        """
        with self._lock:
            # Check if model is available
            if config.validation_enabled and not self.validate_model(config.model_name):
                available = self.get_available_models()
                msg = f"Model '{config.model_name}' not found or unavailable"
                raise VLMModelNotFoundError(msg, model_name=config.model_name, available_models=available)

            # Clean up existing model if any
            if self.loaded_model is not None:
                self.loaded_model.cleanup()

            try:
                start_time = time.time()

                # For now, create a mock model instance
                # In real implementation, this would use MLX VLM loading
                mock_model_instance = f"mock_model_{config.model_name}"

                load_time = time.time() - start_time

                # Create loaded model
                loaded_model = LoadedModel(
                    model_instance=mock_model_instance,
                    model_name=config.model_name,
                    model_version="v1.0",  # Would come from actual model
                    memory_usage=1000000,  # Would be calculated from actual model
                    load_time=load_time,
                    capabilities={"vision": True, "text": True},
                )

                self.loaded_model = loaded_model
                return loaded_model

            except Exception as e:
                msg = f"Failed to load model '{config.model_name}'"
                raise VLMModelLoadError(msg, model_name=config.model_name, error_reason=str(e))

    def get_available_models(self) -> list[str]:
        """
        Get list of known VLM models.

        Returns:
            List[str]: Known model identifiers (MLX-compatible vision models)
        """
        import os

        configured_model = os.getenv("VISION_MODEL")
        default_models = ["mlx-community/GLM-4.6V-Flash-4bit"]

        if configured_model and configured_model not in default_models:
            return [configured_model, *default_models]
        return default_models

    def cleanup_models(self) -> None:
        """Clean up all loaded models."""
        with self._lock:
            if self.loaded_model is not None:
                self.loaded_model.cleanup()
                self.loaded_model = None

            # Clear validation cache
            self.validation_cache.clear()

    def get_current_model(self) -> LoadedModel | None:
        """Get currently loaded model."""
        return self.loaded_model

    def is_model_loaded(self, model_name: str) -> bool:
        """Check if specific model is currently loaded."""
        return self.loaded_model is not None and self.loaded_model.model_name == model_name and self.loaded_model.is_ready


# Global registry instance (singleton pattern)
_global_registry: VLMModelRegistry | None = None
_registry_lock = threading.Lock()


def get_global_registry() -> VLMModelRegistry:
    """Get or create global model registry instance."""
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = VLMModelRegistry()

    return _global_registry
