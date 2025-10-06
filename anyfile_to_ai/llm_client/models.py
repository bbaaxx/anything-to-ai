"""Data models for LLM client.

This module defines the core data structures used by the LLM client,
including messages, requests, responses, and model information.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MessageRole(str, Enum):
    """Message roles in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class FinishReason(str, Enum):
    """Completion finish reasons."""

    STOP = "stop"  # Natural completion
    LENGTH = "length"  # Max tokens reached
    ERROR = "error"  # Error occurred


@dataclass(frozen=True)
class Message:
    """Single message in LLM conversation."""

    role: str
    content: str

    def __post_init__(self):
        """Validate message after initialization."""
        if self.role not in [MessageRole.SYSTEM.value, MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError(f"Invalid message role: {self.role}. Must be one of: system, user, assistant")
        if not self.content or not self.content.strip():
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Message content must not be empty")


@dataclass(frozen=True)
class Usage:
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __post_init__(self):
        """Validate usage statistics."""
        if self.prompt_tokens < 0 or self.completion_tokens < 0 or self.total_tokens < 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Token counts must be non-negative")


@dataclass(frozen=True)
class ModelInfo:
    """Information about an available LLM model."""

    id: str
    provider: str
    object: str = "model"
    created: Optional[int] = None
    owned_by: Optional[str] = None
    context_length: Optional[int] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Validate model info."""
        if not self.id:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Model id must not be empty")
        if self.context_length is not None and self.context_length <= 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Context length must be positive")


@dataclass
class LLMRequest:
    """Request for LLM completion."""

    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    request_id: Optional[str] = None
    timeout_override: Optional[float] = None

    def __post_init__(self):
        """Validate request after initialization."""
        from anyfile_to_ai.llm_client.exceptions import ValidationError

        if not self.messages:
            raise ValidationError("Messages list must not be empty")

        if not any(msg.role == MessageRole.USER.value for msg in self.messages):
            raise ValidationError("At least one message with role='user' is required")

        if not 0.0 <= self.temperature <= 2.0:
            raise ValidationError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")

        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValidationError("max_tokens must be positive")


@dataclass(frozen=True)
class LLMResponse:
    """Response from LLM generation."""

    content: str
    model: str
    finish_reason: str
    response_id: str
    provider: str
    latency_ms: float
    usage: Optional[Usage] = None
    retry_count: int = 0
    used_fallback: bool = False
    fallback_provider: Optional[str] = None

    def __post_init__(self):
        """Validate response after initialization."""
        if self.finish_reason not in [FinishReason.STOP.value, FinishReason.LENGTH.value, FinishReason.ERROR.value]:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError(f"Invalid finish_reason: {self.finish_reason}")

        if self.latency_ms < 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Latency must be non-negative")

        if self.retry_count < 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            raise ValidationError("Retry count must be non-negative")
