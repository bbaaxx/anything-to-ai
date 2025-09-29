"""
API Contract: VLM Integration Interface
Defines the new VLM-specific interfaces for real model integration.
"""

from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass


class VLMModel(Protocol):
    """Protocol for VLM model implementations."""

    def process_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
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
        ...

    def get_model_info(self) -> Dict[str, str]:
        """
        Get model information.

        Returns:
            Dict containing model name, version, capabilities
        """
        ...

    def cleanup(self) -> None:
        """Clean up model resources."""
        ...


@dataclass
class VLMConfiguration:
    """VLM model configuration from environment."""
    model_name: str
    timeout_seconds: int = 60
    timeout_behavior: str = "error"  # "error", "fallback", "continue"
    auto_download: bool = True
    validate_before_load: bool = True
    cache_dir: Optional[str] = None


class VLMModelRegistry:
    """Registry for managing VLM models."""

    def validate_model(self, model_name: str) -> bool:
        """
        Validate model availability.

        Args:
            model_name: VLM model identifier

        Returns:
            bool: True if model available
        """
        ...

    def load_model(self, config: VLMConfiguration) -> VLMModel:
        """
        Load VLM model instance.

        Args:
            config: VLM configuration

        Returns:
            VLMModel: Loaded model instance

        Raises:
            VLMModelLoadError: If model loading fails
            VLMModelNotFoundError: If model not found
        """
        ...

    def get_available_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List[str]: Available model identifiers
        """
        ...

    def cleanup_models(self) -> None:
        """Clean up all loaded models."""
        ...


class VLMProcessor:
    """Main VLM processing interface."""

    def __init__(self, registry: VLMModelRegistry):
        """Initialize with model registry."""
        ...

    def process_image_with_vlm(
        self,
        image_path: str,
        prompt: str,
        config: VLMConfiguration
    ) -> Dict[str, Any]:
        """
        Process single image with VLM.

        Args:
            image_path: Path to image file
            prompt: VLM prompt text
            config: VLM configuration

        Returns:
            Dict containing:
            - description: VLM-generated description
            - confidence_score: Model confidence (if available)
            - processing_time: Time taken for VLM processing
            - model_info: Model name and version used

        Raises:
            VLMProcessingError: If VLM processing fails
            VLMTimeoutError: If processing exceeds timeout
        """
        ...

    def process_batch_with_vlm(
        self,
        image_paths: List[str],
        prompts: List[str],
        config: VLMConfiguration
    ) -> List[Dict[str, Any]]:
        """
        Process batch of images with VLM.

        Args:
            image_paths: List of image file paths
            prompts: List of VLM prompts
            config: VLM configuration

        Returns:
            List[Dict]: VLM results for each image

        Raises:
            VLMProcessingError: If batch processing fails
        """
        ...


# VLM Configuration Contract
VLM_CONFIG_SCHEMA = {
    "model_name": {
        "type": "string",
        "required": True,
        "source": "VISION_MODEL environment variable"
    },
    "timeout_seconds": {
        "type": "integer",
        "default": 60,
        "min": 1,
        "max": 3600
    },
    "timeout_behavior": {
        "type": "string",
        "choices": ["error", "fallback", "continue"],
        "default": "error"
    },
    "auto_download": {
        "type": "boolean",
        "default": True
    },
    "validate_before_load": {
        "type": "boolean",
        "default": True
    },
    "cache_dir": {
        "type": "string",
        "optional": True
    }
}

# VLM Result Schema
VLM_RESULT_SCHEMA = {
    "description": {
        "type": "string",
        "required": True,
        "description": "AI-generated image description"
    },
    "confidence_score": {
        "type": "number",
        "optional": True,
        "range": [0.0, 1.0]
    },
    "processing_time": {
        "type": "number",
        "required": True,
        "description": "VLM processing time in seconds"
    },
    "model_info": {
        "type": "object",
        "required": True,
        "properties": {
            "name": "string",
            "version": "string"
        }
    }
}

# Error Handling Contract
VLM_EXCEPTIONS = {
    "VLMConfigurationError": {
        "base": "ImageProcessingError",
        "when": "Invalid VLM configuration",
        "fields": ["config_issue", "suggested_fix"]
    },
    "VLMModelLoadError": {
        "base": "ImageProcessingError",
        "when": "Model loading failure",
        "fields": ["model_name", "error_reason"]
    },
    "VLMProcessingError": {
        "base": "ImageProcessingError",
        "when": "VLM processing failure",
        "fields": ["image_path", "model_name", "error_details"]
    },
    "VLMTimeoutError": {
        "base": "VLMProcessingError",
        "when": "Processing timeout exceeded",
        "fields": ["timeout_seconds", "actual_time"]
    },
    "VLMModelNotFoundError": {
        "base": "VLMConfigurationError",
        "when": "Specified model not available",
        "fields": ["model_name", "available_models"]
    }
}

# Integration Points Contract
INTEGRATION_POINTS = {
    "environment_config": {
        "function": "load_vlm_config_from_env",
        "returns": "VLMConfiguration",
        "raises": ["VLMConfigurationError"]
    },
    "model_validation": {
        "function": "validate_vlm_model",
        "args": ["model_name"],
        "returns": "bool"
    },
    "enhanced_processing": {
        "function": "process_with_vlm_and_metadata",
        "args": ["image_path", "config"],
        "returns": "enhanced_result",
        "description": "Combines VLM processing with technical metadata"
    },
    "cleanup_hook": {
        "function": "cleanup_vlm_resources",
        "when": "batch_processing_complete",
        "description": "Automatic resource cleanup"
    }
}
