"""VLM configuration loader from environment and integration."""

import os
from typing import Optional

from .config import load_vlm_config_from_env
from .vlm_models import ModelConfiguration
from .vlm_exceptions import VLMConfigurationError


def load_vlm_configuration() -> ModelConfiguration:
    """
    Load VLM configuration from environment variables.

    Returns:
        ModelConfiguration: VLM model configuration

    Raises:
        VLMConfigurationError: If configuration is invalid or missing
    """
    try:
        vlm_config = load_vlm_config_from_env()

        # Convert VLMConfig to ModelConfiguration
        return ModelConfiguration(
            model_name=vlm_config.model_name,
            timeout_seconds=vlm_config.timeout_seconds,
            timeout_behavior=vlm_config.timeout_behavior,
            auto_download=vlm_config.auto_download,
            validation_enabled=vlm_config.validate_before_load,
            cache_dir=vlm_config.cache_dir
        )

    except Exception as e:
        raise VLMConfigurationError(
            f"Failed to load VLM configuration: {str(e)}",
            config_field="VISION_MODEL",
            suggested_fix="Set VISION_MODEL environment variable (e.g., export VISION_MODEL=google/gemma-3-4b)"
        )


def validate_vlm_environment() -> bool:
    """
    Validate that VLM environment is properly configured.

    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        load_vlm_configuration()
        return True
    except VLMConfigurationError:
        return False


def get_model_name_from_env() -> Optional[str]:
    """
    Get model name from environment variable.

    Returns:
        Optional[str]: Model name if set, None otherwise
    """
    return os.getenv('VISION_MODEL')


def is_vlm_enabled() -> bool:
    """
    Check if VLM processing is enabled via environment.

    Returns:
        bool: True if VLM is enabled, False otherwise
    """
    return get_model_name_from_env() is not None


def create_default_vlm_config() -> ModelConfiguration:
    """
    Create default VLM configuration.

    Returns:
        ModelConfiguration: Default configuration

    Raises:
        VLMConfigurationError: If no model name available
    """
    model_name = get_model_name_from_env()
    if not model_name:
        raise VLMConfigurationError(
            "No VLM model configured",
            config_field="VISION_MODEL",
            suggested_fix="Set VISION_MODEL environment variable"
        )

    return ModelConfiguration(
        model_name=model_name,
        timeout_seconds=60,
        timeout_behavior="error",
        auto_download=True,
        validation_enabled=True
    )


def merge_processing_config_with_vlm(processing_config, vlm_config: ModelConfiguration):
    """
    Merge ProcessingConfig with VLM configuration.

    Args:
        processing_config: Existing ProcessingConfig instance
        vlm_config: VLM model configuration

    Returns:
        Updated ProcessingConfig with VLM settings
    """
    # Update model name from VLM config
    processing_config.model_name = vlm_config.model_name

    # Add VLM-specific fields if they don't exist
    if not hasattr(processing_config, 'vlm_timeout_behavior'):
        processing_config.vlm_timeout_behavior = vlm_config.timeout_behavior

    if not hasattr(processing_config, 'auto_download_models'):
        processing_config.auto_download_models = vlm_config.auto_download

    if not hasattr(processing_config, 'validate_model_before_load'):
        processing_config.validate_model_before_load = vlm_config.validation_enabled

    # Override timeout if VLM config specifies it
    if vlm_config.timeout_seconds != 60:  # Not default
        processing_config.timeout_seconds = vlm_config.timeout_seconds

    return processing_config
