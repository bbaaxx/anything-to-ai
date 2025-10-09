"""Enhanced result structures combining VLM and technical metadata."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EnhancedResult:
    """Combined result containing both VLM description and technical metadata."""

    vlm_description: str
    technical_metadata: dict[str, Any]
    model_info: dict[str, str]
    processing_time: float
    confidence_score: float | None = None

    def __post_init__(self):
        """Validate enhanced result after initialization."""
        if not self.vlm_description:
            msg = "vlm_description cannot be empty"
            raise ValueError(msg)

        if self.technical_metadata is None:
            msg = "technical_metadata must be provided"
            raise ValueError(msg)

        if self.processing_time <= 0:
            msg = "processing_time must be positive"
            raise ValueError(msg)

        if self.confidence_score is not None and not (0.0 <= self.confidence_score <= 1.0):
            msg = "confidence_score must be between 0.0 and 1.0"
            raise ValueError(msg)

    @property
    def has_confidence_score(self) -> bool:
        """Check if confidence score is available."""
        return self.confidence_score is not None

    @property
    def model_name(self) -> str:
        """Get model name from model info."""
        return self.model_info.get("name", "unknown")

    @property
    def model_version(self) -> str:
        """Get model version from model info."""
        return self.model_info.get("version", "unknown")

    @property
    def image_format(self) -> str:
        """Get image format from technical metadata."""
        return self.technical_metadata.get("format", "unknown")

    @property
    def image_dimensions(self) -> tuple:
        """Get image dimensions from technical metadata."""
        dims = self.technical_metadata.get("dimensions", [0, 0])
        return tuple(dims) if isinstance(dims, list) else (0, 0)

    @property
    def file_size(self) -> int:
        """Get file size from technical metadata."""
        return self.technical_metadata.get("file_size", 0)

    def to_dict(self) -> dict[str, Any]:
        """Convert enhanced result to dictionary."""
        return {"vlm_description": self.vlm_description, "technical_metadata": self.technical_metadata, "model_info": self.model_info, "processing_time": self.processing_time, "confidence_score": self.confidence_score}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnhancedResult":
        """Create enhanced result from dictionary."""
        return cls(vlm_description=data["vlm_description"], technical_metadata=data["technical_metadata"], model_info=data["model_info"], processing_time=data["processing_time"], confidence_score=data.get("confidence_score"))

    def merge_with_description_result(self, base_result: Any) -> Any:
        """
        Merge enhanced data with existing DescriptionResult.

        Args:
            base_result: Existing DescriptionResult to enhance

        Returns:
            Enhanced DescriptionResult with VLM data
        """
        # Copy all existing fields from base result
        enhanced_data = {}

        # Copy existing attributes
        for attr in ["image_path", "success", "prompt_used"]:
            if hasattr(base_result, attr):
                enhanced_data[attr] = getattr(base_result, attr)

        # Update with VLM data
        enhanced_data.update(
            {
                "description": self.vlm_description,
                "confidence_score": self.confidence_score,
                "processing_time": self.processing_time,
                "model_used": self.model_name,
                "technical_metadata": self.technical_metadata,
                "vlm_processing_time": self.processing_time,
                "model_version": self.model_version,
            },
        )

        # Create new result with enhanced data
        from .models import DescriptionResult

        return DescriptionResult(**enhanced_data)


@dataclass
class VLMProcessingResult:
    """Result of VLM processing operations."""

    description: str
    confidence_score: float | None
    processing_time: float
    model_info: dict[str, str]
    error: str | None = None

    @property
    def success(self) -> bool:
        """Check if VLM processing was successful."""
        return self.error is None and bool(self.description)

    @property
    def has_error(self) -> bool:
        """Check if processing resulted in error."""
        return self.error is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert VLM result to dictionary."""
        return {"description": self.description, "confidence_score": self.confidence_score, "processing_time": self.processing_time, "model_info": self.model_info, "error": self.error, "success": self.success}
