"""LLM Client - Unified interface for local LLM services.

This module provides a unified interface for interacting with multiple LLM service
providers including Ollama, LM Studio, and MLX-optimized models.
"""

from anyfile_to_ai.llm_client.client import LLMClient
from anyfile_to_ai.llm_client.config import LLMConfig, Provider
from anyfile_to_ai.llm_client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    GenerationError,
    LLMError,
    ModelNotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from anyfile_to_ai.llm_client.models import (
    FinishReason,
    LLMRequest,
    LLMResponse,
    Message,
    MessageRole,
    ModelInfo,
    Usage,
)

__version__ = "0.1.0"

__all__ = [
    "AuthenticationError",
    "ConfigurationError",
    "ConnectionError",
    "FinishReason",
    "GenerationError",
    # Main client
    "LLMClient",
    # Configuration
    "LLMConfig",
    # Exceptions
    "LLMError",
    "LLMRequest",
    "LLMResponse",
    # Models
    "Message",
    "MessageRole",
    "ModelInfo",
    "ModelNotFoundError",
    "Provider",
    "RateLimitError",
    "TimeoutError",
    "Usage",
    "ValidationError",
    # Version
    "__version__",
]
