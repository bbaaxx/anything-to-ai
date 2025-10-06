"""Model validation and loading logic for VLM integration."""

from typing import List, Optional, Dict, Any

from .vlm_models import ModelConfiguration
from .model_registry import LoadedModel, get_global_registry
from .vlm_exceptions import VLMModelNotFoundError


class ModelLoader:
    """Handles VLM model validation and loading operations."""

    def __init__(self):
        self.registry = get_global_registry()
        self._validation_cache: Dict[str, bool] = {}

    def validate_model_availability(self, model_name: str) -> bool:
        """
        Validate that specified VLM model is available.

        Args:
            model_name: VLM model identifier

        Returns:
            bool: True if model available, False otherwise
        """
        return self.registry.validate_model(model_name)

    def get_available_models(self) -> List[str]:
        """
        Get list of available VLM models.

        Returns:
            List[str]: Available VLM model identifiers
        """
        return self.registry.get_available_models()

    def load_model_if_needed(self, config: ModelConfiguration) -> LoadedModel:
        """
        Load VLM model if not already loaded.

        Args:
            config: VLM model configuration

        Returns:
            LoadedModel: Loaded model instance

        Raises:
            VLMModelLoadError: If model loading fails
            VLMModelNotFoundError: If model not found
        """
        # Check if model is already loaded
        if self.registry.is_model_loaded(config.model_name):
            return self.registry.get_current_model()

        # Load new model
        return self.registry.load_model(config)

    def validate_and_load_model(self, config: ModelConfiguration) -> LoadedModel:
        """
        Validate model availability and load it.

        Args:
            config: VLM model configuration

        Returns:
            LoadedModel: Loaded and validated model

        Raises:
            VLMModelNotFoundError: If model validation fails
            VLMModelLoadError: If model loading fails
        """
        # Validate model first if required
        if config.validation_enabled:
            if not self.validate_model_availability(config.model_name):
                available_models = self.get_available_models()
                raise VLMModelNotFoundError(
                    f"Model '{config.model_name}' is not available",
                    model_name=config.model_name,
                    available_models=available_models,
                    suggested_fix=f"Try one of: {', '.join(available_models[:3])}"
                )

        # Load the model
        return self.load_model_if_needed(config)

    def preload_model(self, model_name: str, **kwargs) -> LoadedModel:
        """
        Preload a model for faster processing.

        Args:
            model_name: VLM model identifier
            **kwargs: Additional configuration options

        Returns:
            LoadedModel: Preloaded model instance
        """
        config = ModelConfiguration(
            model_name=model_name,
            validation_enabled=kwargs.get('validate', True),
            auto_download=kwargs.get('auto_download', True),
            **kwargs
        )

        return self.validate_and_load_model(config)

    def check_model_compatibility(self, model_name: str) -> Dict[str, Any]:
        """
        Check model compatibility and requirements.

        Args:
            model_name: VLM model identifier

        Returns:
            Dict containing compatibility information
        """
        compatibility_info = {
            "model_name": model_name,
            "available": False,
            "compatible": False,
            "requirements_met": False,
            "issues": []
        }

        try:
            # Check availability
            if self.validate_model_availability(model_name):
                compatibility_info["available"] = True

                # Check MLX compatibility (for now, assume all models are compatible)
                compatibility_info["compatible"] = True
                compatibility_info["requirements_met"] = True

            else:
                compatibility_info["issues"].append("Model not available")

        except Exception as e:
            compatibility_info["issues"].append(f"Validation error: {str(e)}")

        return compatibility_info

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed model information.

        Args:
            model_name: VLM model identifier

        Returns:
            Optional[Dict]: Model information if available
        """
        try:
            if not self.validate_model_availability(model_name):
                return None

            # For now, return basic info
            # Real implementation would query model metadata
            return {
                "name": model_name,
                "type": "VLM",
                "framework": "MLX",
                "capabilities": ["vision", "text"],
                "estimated_memory": "1GB",  # Would be model-specific
                "supported_formats": ["JPEG", "PNG", "WEBP"]
            }

        except Exception:
            return None

    def cleanup_unused_models(self):
        """Clean up models that are no longer needed."""
        self.registry.cleanup_models()

    def get_loading_progress(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model loading progress if available.

        Args:
            model_name: VLM model identifier

        Returns:
            Optional[Dict]: Loading progress information
        """
        # For now, return None (no progress tracking)
        # Real implementation would track download/loading progress
        return None


# Global model loader instance
_global_loader: Optional[ModelLoader] = None


def get_global_model_loader() -> ModelLoader:
    """Get or create global model loader instance."""
    global _global_loader

    if _global_loader is None:
        _global_loader = ModelLoader()

    return _global_loader


# Convenience functions for external use
def validate_model_availability(model_name: str) -> bool:
    """Validate that specified VLM model is available."""
    loader = get_global_model_loader()
    return loader.validate_model_availability(model_name)


def get_available_models() -> List[str]:
    """Get list of available VLM models."""
    loader = get_global_model_loader()
    return loader.get_available_models()


def load_model_for_processing(config: ModelConfiguration) -> LoadedModel:
    """Load and validate model for processing."""
    loader = get_global_model_loader()
    return loader.validate_and_load_model(config)
