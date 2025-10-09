"""VLM model entities and configuration classes."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ModelConfiguration:
    """VLM model configuration entity."""

    model_name: str
    timeout_seconds: int = 60
    timeout_behavior: str = "error"  # "error", "fallback", "continue"
    auto_download: bool = True
    validation_enabled: bool = True
    cache_dir: str | None = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.model_name or not self.model_name.strip():
            msg = "model_name cannot be empty"
            raise ValueError(msg)

        if self.timeout_seconds <= 0:
            msg = "timeout_seconds must be positive"
            raise ValueError(msg)

        if self.timeout_behavior not in ["error", "fallback", "continue"]:
            msg = "timeout_behavior must be 'error', 'fallback', or 'continue'"
            raise ValueError(msg)

    @property
    def is_configured(self) -> bool:
        """Check if configuration is valid for VLM processing."""
        return bool(self.model_name and self.model_name.strip())

    @property
    def should_validate_before_load(self) -> bool:
        """Check if model should be validated before loading."""
        return self.validation_enabled

    @property
    def should_auto_download(self) -> bool:
        """Check if models should be automatically downloaded."""
        return self.auto_download

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {"model_name": self.model_name, "timeout_seconds": self.timeout_seconds, "timeout_behavior": self.timeout_behavior, "auto_download": self.auto_download, "validation_enabled": self.validation_enabled, "cache_dir": self.cache_dir}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfiguration":
        """Create configuration from dictionary."""
        return cls(
            model_name=data["model_name"],
            timeout_seconds=data.get("timeout_seconds", 60),
            timeout_behavior=data.get("timeout_behavior", "error"),
            auto_download=data.get("auto_download", True),
            validation_enabled=data.get("validation_enabled", True),
            cache_dir=data.get("cache_dir"),
        )
