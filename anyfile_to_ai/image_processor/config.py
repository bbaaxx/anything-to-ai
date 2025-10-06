"""Environment configuration and validation for VLM integration."""

import os
from typing import Optional
from dataclasses import dataclass

from .exceptions import ValidationError


@dataclass
class VLMConfig:
    """Configuration for VLM model processing."""
    model_name: str
    timeout_seconds: int = 60
    timeout_behavior: str = "error"  # "error", "fallback", "continue"
    auto_download: bool = True
    validate_before_load: bool = True
    cache_dir: Optional[str] = None


def validate_vision_model_env() -> str:
    """
    Validate VISION_MODEL environment variable.

    Returns:
        str: Model name from environment variable

    Raises:
        ValidationError: If VISION_MODEL not set or invalid
    """
    model_name = os.getenv('VISION_MODEL')

    if not model_name:
        raise ValidationError(
            "VISION_MODEL environment variable not set. "
            "Please configure a VLM model (e.g., export VISION_MODEL=google/gemma-3-4b)",
            "VISION_MODEL"
        )

    if not model_name.strip():
        raise ValidationError(
            "VISION_MODEL environment variable is empty",
            "VISION_MODEL"
        )

    return model_name.strip()


def load_vlm_config_from_env() -> VLMConfig:
    """
    Load VLM configuration from environment variables.

    Returns:
        VLMConfig: Configuration object with environment settings

    Raises:
        ValidationError: If required configuration is missing or invalid
    """
    model_name = validate_vision_model_env()

    # Load optional environment variables with defaults
    timeout_seconds = _parse_env_int('VLM_TIMEOUT_SECONDS', 60, min_val=1, max_val=3600)
    timeout_behavior = _parse_env_choice('VLM_TIMEOUT_BEHAVIOR', 'error',
                                        ['error', 'fallback', 'continue'])
    auto_download = _parse_env_bool('VLM_AUTO_DOWNLOAD', True)
    validate_before_load = _parse_env_bool('VLM_VALIDATE_BEFORE_LOAD', True)
    cache_dir = os.getenv('VLM_CACHE_DIR')

    return VLMConfig(
        model_name=model_name,
        timeout_seconds=timeout_seconds,
        timeout_behavior=timeout_behavior,
        auto_download=auto_download,
        validate_before_load=validate_before_load,
        cache_dir=cache_dir
    )


def _parse_env_int(var_name: str, default: int, min_val: int = None, max_val: int = None) -> int:
    """Parse integer from environment variable with validation."""
    value = os.getenv(var_name)
    if value is None:
        return default

    try:
        parsed = int(value)
        if min_val is not None and parsed < min_val:
            raise ValidationError(f"{var_name} must be >= {min_val}", var_name)
        if max_val is not None and parsed > max_val:
            raise ValidationError(f"{var_name} must be <= {max_val}", var_name)
        return parsed
    except ValueError:
        raise ValidationError(f"{var_name} must be a valid integer", var_name)


def _parse_env_bool(var_name: str, default: bool) -> bool:
    """Parse boolean from environment variable."""
    value = os.getenv(var_name)
    if value is None:
        return default

    if value.lower() in ('true', '1', 'yes', 'on'):
        return True
    elif value.lower() in ('false', '0', 'no', 'off'):
        return False
    else:
        raise ValidationError(f"{var_name} must be true/false", var_name)


def _parse_env_choice(var_name: str, default: str, choices: list) -> str:
    """Parse choice from environment variable with validation."""
    value = os.getenv(var_name)
    if value is None:
        return default

    if value not in choices:
        raise ValidationError(f"{var_name} must be one of {choices}", var_name)

    return value
