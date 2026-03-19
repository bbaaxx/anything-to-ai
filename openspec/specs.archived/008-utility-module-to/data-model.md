# Data Model: LLM Utility Module

**Feature**: 008-utility-module-to
**Date**: 2025-09-30
**Status**: Design Complete

## Overview

This document defines the data structures for the LLM utility module. All models use Python dataclasses for simplicity and immutability where appropriate.

---

## Core Entities

### 1. LLMConfig

**Purpose**: Configuration for connecting to an LLM service provider

**Attributes**:
```python
@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM service connection."""

    provider: str                    # Provider type: "ollama", "lmstudio", "mlx"
    base_url: str                    # Base API URL (e.g., "http://localhost:11434")
    api_key: Optional[str] = None    # API key (optional for local services)
    timeout: float = 30.0            # Request timeout in seconds
    verify_ssl: bool = True          # SSL certificate verification

    # Retry configuration
    max_retries: int = 3            # Maximum retry attempts
    retry_delay: float = 1.0        # Base retry delay in seconds
    retry_max_delay: float = 10.0   # Maximum retry delay
    retry_exponential_base: float = 2.0  # Exponential backoff base

    # Cache configuration
    cache_ttl: int = 300            # Model list cache TTL in seconds (5 min default)

    # Fallback configuration
    fallback_configs: Optional[List['LLMConfig']] = None  # Ordered fallback providers
```

**Validation Rules**:
- `provider` must be one of: "ollama", "lmstudio", "mlx"
- `base_url` must be valid URL format
- `timeout` must be > 0
- `max_retries` must be >= 0
- `cache_ttl` must be >= 0 (0 = no cache)

**Relationships**:
- Has zero or more `fallback_configs` (LLMConfig instances)
- Used by `LLMClient` for initialization

---

### 2. Message

**Purpose**: Represents a single message in a conversation

**Attributes**:
```python
@dataclass(frozen=True)
class Message:
    """Single message in LLM conversation."""

    role: str        # One of: "system", "user", "assistant"
    content: str     # Message content
```

**Validation Rules**:
- `role` must be one of: "system", "user", "assistant"
- `content` must not be empty

**Relationships**:
- Multiple messages form a conversation in `LLMRequest`

---

### 3. LLMRequest

**Purpose**: Request to generate completion from LLM

**Attributes**:
```python
@dataclass
class LLMRequest:
    """Request for LLM completion."""

    messages: List[Message]          # Conversation messages
    model: Optional[str] = None      # Model name (None = provider default)
    temperature: float = 0.7         # Sampling temperature (0.0-2.0)
    max_tokens: Optional[int] = None # Maximum tokens to generate
    stream: bool = False             # Enable streaming responses (future)

    # Request metadata
    request_id: Optional[str] = None # Unique request identifier
    timeout_override: Optional[float] = None  # Override default timeout
```

**Validation Rules**:
- `messages` must not be empty
- `temperature` must be in range [0.0, 2.0]
- `max_tokens` must be > 0 if provided
- At least one message with role="user" required

**Relationships**:
- Contains one or more `Message` instances
- Processed by `LLMClient.generate()` → produces `LLMResponse`

---

### 4. Usage

**Purpose**: Token usage statistics from LLM response

**Attributes**:
```python
@dataclass(frozen=True)
class Usage:
    """Token usage statistics."""

    prompt_tokens: int      # Tokens in prompt
    completion_tokens: int  # Tokens in completion
    total_tokens: int       # Total tokens used
```

**Validation Rules**:
- All values must be >= 0
- `total_tokens` should equal `prompt_tokens + completion_tokens`

**Relationships**:
- Part of `LLMResponse`

---

### 5. LLMResponse

**Purpose**: Response from LLM generation

**Attributes**:
```python
@dataclass(frozen=True)
class LLMResponse:
    """Response from LLM generation."""

    content: str                     # Generated text content
    model: str                       # Model that generated response
    finish_reason: str               # Completion reason: "stop", "length", "error"
    usage: Optional[Usage] = None    # Token usage (if available)

    # Response metadata
    response_id: str                 # Unique response identifier
    provider: str                    # Provider that handled request
    latency_ms: float                # Request latency in milliseconds

    # Error tracking
    retry_count: int = 0             # Number of retries performed
    used_fallback: bool = False      # Whether fallback provider was used
    fallback_provider: Optional[str] = None  # Fallback provider used (if any)
```

**Validation Rules**:
- `finish_reason` must be one of: "stop", "length", "error"
- `latency_ms` must be >= 0
- `retry_count` must be >= 0

**Relationships**:
- Returned by `LLMClient.generate()`
- Contains optional `Usage` instance

---

### 6. ModelInfo

**Purpose**: Information about available LLM model

**Attributes**:
```python
@dataclass(frozen=True)
class ModelInfo:
    """Information about an available LLM model."""

    id: str                          # Model identifier
    provider: str                    # Provider name
    object: str = "model"            # Object type (OpenAI compatibility)
    created: Optional[int] = None    # Creation timestamp
    owned_by: Optional[str] = None   # Owner organization

    # Extended metadata (provider-specific)
    context_length: Optional[int] = None  # Maximum context length
    description: Optional[str] = None     # Human-readable description
```

**Validation Rules**:
- `id` must not be empty
- `context_length` must be > 0 if provided

**Relationships**:
- Returned in list by `LLMClient.list_models()`

---

## Error Models

### 7. LLMError

**Purpose**: Base exception class for all LLM client errors

**Attributes**:
```python
class LLMError(Exception):
    """Base exception for LLM client errors."""

    def __init__(self, message: str, provider: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
```

**Subclasses**:
- `ConfigurationError`: Invalid configuration
- `ConnectionError`: Service unreachable
- `AuthenticationError`: API key invalid or missing
- `ModelNotFoundError`: Requested model not available
- `RateLimitError`: Rate limit exceeded
- `TimeoutError`: Request timed out
- `ValidationError`: Invalid request data
- `GenerationError`: Error during generation

---

## Enumerations

### 8. Provider (Enum)

```python
class Provider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    MLX = "mlx"
```

### 9. MessageRole (Enum)

```python
class MessageRole(str, Enum):
    """Message roles in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
```

### 10. FinishReason (Enum)

```python
class FinishReason(str, Enum):
    """Completion finish reasons."""

    STOP = "stop"          # Natural completion
    LENGTH = "length"      # Max tokens reached
    ERROR = "error"        # Error occurred
```

---

## Relationships Diagram

```
LLMConfig ──(0..*)──> LLMConfig (fallback_configs)
    │
    ├──> LLMClient (uses for initialization)
    │
LLMRequest ──(1..*)──> Message
    │
    └──> LLMClient.generate()
             │
             └──> LLMResponse ──(0..1)──> Usage

LLMClient.list_models() ──> List[ModelInfo]
```

---

## State Transitions

### LLMRequest Lifecycle

```
[Created] → [Validated] → [Submitted] → [Processing] → [Completed]
                                              │
                                              ├──> [Retry] (if error + retries remain)
                                              │       └──> [Processing]
                                              │
                                              └──> [Fallback] (if all retries failed + fallback exists)
                                                      └──> [Processing] (with fallback provider)
```

### Model List Cache Lifecycle

```
[Empty] → [Fetching] → [Cached] → [Valid]
                          │          │
                          │          └──> (TTL expires) → [Stale] → [Fetching]
                          │
                          └──> [Invalidated] → [Empty]
```

---

## File Size Estimates

| File | Estimated Lines | Within 250 Limit? |
|------|----------------|-------------------|
| `models.py` | ~180 | ✅ Yes |
| `config.py` | ~80 | ✅ Yes |
| `exceptions.py` | ~120 | ✅ Yes |
| `client.py` | ~200 | ✅ Yes |
| `cache.py` | ~100 | ✅ Yes |
| `retry.py` | ~150 | ✅ Yes |
| `adapters/base.py` | ~60 | ✅ Yes |
| `adapters/ollama_adapter.py` | ~120 | ✅ Yes |
| `adapters/lmstudio_adapter.py` | ~120 | ✅ Yes |
| `adapters/mlx_adapter.py` | ~180 | ✅ Yes |

**Total estimated**: ~1,310 lines across 10 files
**Average per file**: ~131 lines
**Constitution compliance**: ✅ All files under 250-line limit

---

## Immutability Strategy

- **Frozen dataclasses**: `LLMConfig`, `Message`, `LLMResponse`, `Usage`, `ModelInfo`
- **Mutable**: `LLMRequest` (to allow modification before submission)
- **Thread-safe**: Cache implementation uses `threading.Lock`

---

## Validation Strategy

- **Config validation**: On `LLMConfig` creation
- **Request validation**: Before submission to provider
- **Response validation**: After receiving from provider
- **Type safety**: Python type hints + runtime checks

---

## Next: Contracts

With data model defined, proceed to create:
1. API contracts in `contracts/` directory
2. Contract tests for each interface
3. Quickstart guide demonstrating usage
