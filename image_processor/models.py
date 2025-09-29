"""Data models for image VLM processing module."""

from dataclasses import dataclass
from typing import List, Optional, Callable

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
    model_name: str = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
    description_style: str = "detailed"
    max_description_length: int = 500
    batch_size: int = 4
    progress_callback: Optional[ProgressCallback] = None
    prompt_template: str = "Describe this image in a {style} manner."
    timeout_seconds: int = 60
