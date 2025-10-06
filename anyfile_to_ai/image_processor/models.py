"""Data models for image VLM processing module."""

import os
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any

# Progress callback type
ProgressCallback = Callable[[int, int], None]


@dataclass
class ImageDocument:
    """Represents an image file with metadata for processing."""
    file_path: str
    format: str
    width: int
    height: int
    file_size: int
    is_large_image: bool


@dataclass
class DescriptionResult:
    """Contains generated text description with processing metadata."""
    image_path: str
    description: str
    confidence_score: Optional[float]
    processing_time: float
    model_used: str
    prompt_used: str
    success: bool
    # Enhanced VLM fields
    technical_metadata: Optional[Dict[str, Any]] = None
    vlm_processing_time: Optional[float] = None
    model_version: Optional[str] = None


@dataclass
class ProcessingResult:
    """Complete result of image processing operation."""
    success: bool
    results: List[DescriptionResult]
    total_images: int
    successful_count: int
    failed_count: int
    total_processing_time: float
    error_message: Optional[str] = None


@dataclass
class ProcessingConfig:
    """Configuration settings for VLM processing."""
    model_name: str = ""  # Will be populated from VISION_MODEL env var
    description_style: str = "detailed"
    max_description_length: int = 500
    batch_size: int = 4
    progress_callback: Optional[ProgressCallback] = None
    prompt_template: str = "Describe this image in a {style} manner."
    timeout_seconds: int = 60
    # Enhanced VLM fields
    vlm_timeout_behavior: str = "error"  # "error", "fallback", "continue"
    auto_download_models: bool = True
    validate_model_before_load: bool = True

    def __post_init__(self):
        """Populate model_name from environment if not set."""
        if not self.model_name:
            from .vlm_exceptions import VLMConfigurationError

            model_name = os.getenv('VISION_MODEL')
            if not model_name:
                raise VLMConfigurationError(
                    "VISION_MODEL environment variable not set",
                    config_field="VISION_MODEL",
                    suggested_fix="Set VISION_MODEL environment variable (e.g., export VISION_MODEL=google/gemma-3-4b)"
                )
            self.model_name = model_name.strip()
