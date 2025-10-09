"""Data models for LLM client.

This module defines the core data structures used by the LLM client,
including messages, requests, responses, and model information.
"""

from dataclasses import dataclass
from enum import Enum


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
        if self.role not in [
            MessageRole.SYSTEM.value,
            MessageRole.USER.value,
            MessageRole.ASSISTANT.value,
        ]:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = f"Invalid message role: {self.role}. Must be one of: system, user, assistant"
            raise ValidationError(msg)
        if not self.content or not self.content.strip():
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = "Message content must not be empty"
            raise ValidationError(msg)


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

            msg = "Token counts must be non-negative"
            raise ValidationError(msg)


@dataclass(frozen=True)
class ModelInfo:
    """Information about an available LLM model."""

    id: str
    provider: str
    object: str = "model"
    created: int | None = None
    owned_by: str | None = None
    context_length: int | None = None
    description: str | None = None

    def __post_init__(self):
        """Validate model info."""
        if not self.id:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = "Model id must not be empty"
            raise ValidationError(msg)
        if self.context_length is not None and self.context_length <= 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = "Context length must be positive"
            raise ValidationError(msg)


@dataclass
class LLMRequest:
    """Request for LLM completion."""

    messages: list[Message]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = False
    request_id: str | None = None
    timeout_override: float | None = None

    def __post_init__(self):
        """Validate request after initialization."""
        from anyfile_to_ai.llm_client.exceptions import ValidationError

        if not self.messages:
            msg = "Messages list must not be empty"
            raise ValidationError(msg)

        if not any(msg.role == MessageRole.USER.value for msg in self.messages):
            msg = "At least one message with role='user' is required"
            raise ValidationError(msg)

        if not 0.0 <= self.temperature <= 2.0:
            msg = f"Temperature must be between 0.0 and 2.0, got {self.temperature}"
            raise ValidationError(msg)

        if self.max_tokens is not None and self.max_tokens <= 0:
            msg = "max_tokens must be positive"
            raise ValidationError(msg)


@dataclass(frozen=True)
class LLMResponse:
    """Response from LLM generation."""

    content: str
    model: str
    finish_reason: str
    response_id: str
    provider: str
    latency_ms: float
    usage: Usage | None = None
    retry_count: int = 0
    used_fallback: bool = False
    fallback_provider: str | None = None

    def __post_init__(self):
        """Validate response after initialization."""
        if self.finish_reason not in [
            FinishReason.STOP.value,
            FinishReason.LENGTH.value,
            FinishReason.ERROR.value,
        ]:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = f"Invalid finish_reason: {self.finish_reason}"
            raise ValidationError(msg)

        if self.latency_ms < 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = "Latency must be non-negative"
            raise ValidationError(msg)

        if self.retry_count < 0:
            from anyfile_to_ai.llm_client.exceptions import ValidationError

            msg = "Retry count must be non-negative"
            raise ValidationError(msg)
