"""Configuration for LLM client.

This module defines configuration structures for connecting to LLM service providers,
including retry, caching, and fallback settings.
"""

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class Provider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    MLX = "mlx"


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM service connection."""

    provider: str
    base_url: str
    api_key: str | None = None
    timeout: float = 30.0
    verify_ssl: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_max_delay: float = 10.0
    retry_exponential_base: float = 2.0
    cache_ttl: int = 300
    fallback_configs: list["LLMConfig"] | None = None

    def __post_init__(self):
        """Validate configuration after initialization."""

        self._validate_provider()
        self._validate_base_url()
        self._validate_numeric_fields()

    def _validate_provider(self):
        """Validate provider is supported."""
        from anything_to_ai.llm_client.exceptions import ValidationError

        valid_providers = [
            Provider.OLLAMA.value,
            Provider.LMSTUDIO.value,
            Provider.MLX.value,
        ]
        if self.provider not in valid_providers:
            raise ValidationError(f"Invalid provider: {self.provider}. Must be one of: {', '.join(valid_providers)}")

    def _validate_base_url(self):
        """Validate base_url format."""
        from anything_to_ai.llm_client.exceptions import ValidationError

        if not self.base_url:
            raise ValidationError("base_url must not be empty")

        # For non-local providers, validate URL structure
        if self.provider != Provider.MLX.value:
            try:
                parsed = urlparse(self.base_url)
                if not parsed.scheme or not (parsed.netloc or parsed.path):
                    raise ValidationError(f"Invalid base_url format: {self.base_url}. Must be a valid URL (e.g., http://localhost:11434)")
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Invalid base_url: {self.base_url}") from e

    def _validate_numeric_fields(self):
        """Validate numeric configuration fields."""
        from anything_to_ai.llm_client.exceptions import ValidationError

        if self.timeout <= 0:
            raise ValidationError(f"timeout must be positive, got {self.timeout}")

        if self.max_retries < 0:
            raise ValidationError(f"max_retries must be non-negative, got {self.max_retries}")

        if self.retry_delay < 0:
            raise ValidationError(f"retry_delay must be non-negative, got {self.retry_delay}")

        if self.retry_max_delay < 0:
            raise ValidationError(f"retry_max_delay must be non-negative, got {self.retry_max_delay}")

        if self.retry_exponential_base <= 0:
            raise ValidationError(f"retry_exponential_base must be positive, got {self.retry_exponential_base}")

        if self.cache_ttl < 0:
            raise ValidationError(f"cache_ttl must be non-negative, got {self.cache_ttl}")
