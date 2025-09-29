"""VLM model registry and loaded model management."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
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
    capabilities: Dict[str, Any]

    @property
    def is_ready(self) -> bool:
        """Check if model is ready for processing."""
        return self.model_instance is not None

    @property
    def model_info(self) -> Dict[str, str]:
        """Get model information dictionary."""
        return {
            "name": self.model_name,
            "version": self.model_version
        }

    def cleanup(self) -> None:
        """Clean up model resources."""
        if self.model_instance is not None:
            # MLX models can be cleaned up by setting to None
            # The garbage collector will handle the rest
            self.model_instance = None


class VLMModelRegistry:
    """Registry for managing VLM models and their lifecycle."""

    def __init__(self):
        self.available_models: Dict[str, Dict[str, Any]] = {}
        self.loaded_model: Optional[LoadedModel] = None
        self.validation_cache: Dict[str, bool] = {}
        self._lock = threading.Lock()

    def validate_model(self, model_name: str) -> bool:
        """
        Validate that specified VLM model is available.

        Args:
            model_name: VLM model identifier

        Returns:
            bool: True if model available, False otherwise
        """
        # Check cache first
        if model_name in self.validation_cache:
            return self.validation_cache[model_name]

        # For now, implement basic validation
        # In real implementation, this would check MLX VLM model availability
        try:
            # Basic validation - check if model name format is reasonable
            if not model_name or '/' not in model_name:
                self.validation_cache[model_name] = False
                return False

            # Accept google/gemma models and mlx-community models
            if (model_name.startswith('google/gemma') or
                model_name.startswith('mlx-community/')):
                self.validation_cache[model_name] = True
                return True

            # For other models, assume validation would check actual availability
            # This would involve checking MLX VLM model repositories
            self.validation_cache[model_name] = False
            return False

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
                raise VLMModelNotFoundError(
                    f"Model '{config.model_name}' not found or unavailable",
                    model_name=config.model_name,
                    available_models=available
                )

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
                    capabilities={"vision": True, "text": True}
                )

                self.loaded_model = loaded_model
                return loaded_model

            except Exception as e:
                raise VLMModelLoadError(
                    f"Failed to load model '{config.model_name}'",
                    model_name=config.model_name,
                    error_reason=str(e)
                )

    def get_available_models(self) -> List[str]:
        """
        Get list of available VLM models.

        Returns:
            List[str]: Available model identifiers
        """
        # For testing purposes, return some mock models
        # In real implementation, this would query MLX VLM repositories
        return [
            "google/gemma-3-4b",
            "google/gemma-3-8b",
            "meta/llama-vision-7b"
        ]

    def cleanup_models(self) -> None:
        """Clean up all loaded models."""
        with self._lock:
            if self.loaded_model is not None:
                self.loaded_model.cleanup()
                self.loaded_model = None

            # Clear validation cache
            self.validation_cache.clear()

    def get_current_model(self) -> Optional[LoadedModel]:
        """Get currently loaded model."""
        return self.loaded_model

    def is_model_loaded(self, model_name: str) -> bool:
        """Check if specific model is currently loaded."""
        return (self.loaded_model is not None and
                self.loaded_model.model_name == model_name and
                self.loaded_model.is_ready)


# Global registry instance (singleton pattern)
_global_registry: Optional[VLMModelRegistry] = None
_registry_lock = threading.Lock()


def get_global_registry() -> VLMModelRegistry:
    """Get or create global model registry instance."""
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = VLMModelRegistry()

    return _global_registry
