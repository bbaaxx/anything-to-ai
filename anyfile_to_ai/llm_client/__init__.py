"""LLM Client - Unified interface for local LLM services.

This module provides a unified interface for interacting with multiple LLM service
providers including Ollama, LM Studio, and MLX-optimized models.
"""

from anything_to_ai.llm_client.client import LLMClient
from anything_to_ai.llm_client.config import LLMConfig, Provider
from anything_to_ai.llm_client.exceptions import (
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
from anything_to_ai.llm_client.models import (
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
    # Main client
    "LLMClient",
    # Configuration
    "LLMConfig",
    "Provider",
    # Models
    "Message",
    "MessageRole",
    "LLMRequest",
    "LLMResponse",
    "ModelInfo",
    "Usage",
    "FinishReason",
    # Exceptions
    "LLMError",
    "ConfigurationError",
    "ConnectionError",
    "AuthenticationError",
    "ModelNotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    "GenerationError",
    # Version
    "__version__",
]
