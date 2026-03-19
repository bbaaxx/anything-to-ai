# Phase 0: Research & Technical Decisions

**Feature**: LLM Utility Module
**Date**: 2025-09-30
**Status**: Complete

## Research Questions

### 1. OpenAI-Compatible Client Library Selection

**Question**: Which library should we use for OpenAI-compatible API calls?

**Options Evaluated**:
- **A. OpenAI Python SDK** (`openai` package)
- **B. httpx** (async HTTP client)
- **C. urllib** (standard library)

**Decision**: **httpx** with fallback capability to urllib

**Rationale**:
- **httpx** provides clean async/sync support, retry mechanisms, and connection pooling
- Lighter than full OpenAI SDK (minimal dependencies principle)
- Better control over request/response handling for multi-provider support
- Can still use urllib for ultra-minimal dependency footprint if needed
- OpenAI SDK is provider-specific; we need generic OpenAI-compatible API support

**Alternatives Considered**:
- OpenAI SDK: Too opinionated for multi-provider use; adds unnecessary abstractions
- urllib only: Lacks retry logic, connection pooling, clean async support
- requests: Synchronous only, being superseded by httpx in modern Python

**Implementation Notes**:
- Use httpx for primary implementation
- Keep adapter interface abstract enough to swap to urllib if needed
- Leverage httpx timeout, retry, and connection management features

---

### 2. Model Listing Cache Strategy

**Question**: How should we cache model listings for performance?

**Options Evaluated**:
- **A. In-memory dict with TTL**
- **B. functools.lru_cache**
- **C. Persistent cache (file/sqlite)**
- **D. No caching**

**Decision**: **In-memory dict with configurable TTL** (default 5 minutes)

**Rationale**:
- Simple to implement within 250-line constraint
- No external dependencies (standard library only)
- Configurable expiration allows fresh data without excessive API calls
- Thread-safe using threading.Lock
- No persistent storage requirement per spec

**Alternatives Considered**:
- lru_cache: Lacks TTL support, difficult to invalidate
- Persistent cache: Adds complexity, unnecessary for single-user local execution
- No caching: Would violate performance goals (< 100ms for cached calls)

**Implementation Notes**:
- Cache structure: `{provider_url: {"models": [...], "expires_at": timestamp}}`
- Separate cache per provider base URL
- Provide manual invalidation method for users
- Cache miss triggers fresh API call with automatic cache update

---

### 3. Retry and Fallback Mechanism

**Question**: How should retry logic and service fallback be implemented?

**Options Evaluated**:
- **A. Decorator-based retry with tenacity library**
- **B. Custom retry logic with exponential backoff**
- **C. httpx built-in retry with custom fallback**
- **D. Simple try/except with configurable fallback list**

**Decision**: **Custom retry with exponential backoff + configurable fallback list**

**Rationale**:
- Keeps dependencies minimal (no tenacity)
- Full control over retry behavior (attempts, backoff, jitter)
- Fallback list allows users to configure provider priority
- Can be implemented in < 250 lines in retry.py
- Explicit is better than implicit (Python principle)

**Alternatives Considered**:
- tenacity: Adds external dependency for simple functionality
- httpx retry only: Doesn't handle cross-provider fallback
- No retry: Would violate resilience requirements

**Implementation Notes**:
- Retry config: `max_attempts=3`, `base_delay=1.0s`, `max_delay=10.0s`, `exponential_base=2`
- Fallback config: ordered list of provider configs `[primary, secondary, tertiary]`
- Failures tracked and reported in response metadata
- Configurable per-request or global defaults

---

### 4. OpenAI Chat Completions API Best Practices

**Question**: What are the key patterns for `/v1/chat/completions` endpoint?

**Research Findings**:

**Standard Request Format**:
```json
{
  "model": "model-name",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": false
}
```

**Standard Response Format**:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "model-name",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

**Model Listing Endpoint**: `/v1/models`
```json
{
  "object": "list",
  "data": [
    {
      "id": "model-name",
      "object": "model",
      "created": 1234567890,
      "owned_by": "organization"
    }
  ]
}
```

**Authentication**:
- Header: `Authorization: Bearer {api_key}`
- Some local services (Ollama) don't require auth
- API key should be optional in config

**Error Response Format**:
```json
{
  "error": {
    "message": "error description",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

**Implementation Notes**:
- Support both authenticated and unauthenticated requests
- Parse standard error responses for better error messages
- Extract usage metadata from responses for observability
- Handle streaming responses (may add in future iteration)

---

### 5. Integration with Existing MLX Code

**Question**: How should the utility integrate with existing `image_processor` MLX usage?

**Current MLX Integration** (from `image_processor/__init__.py`):
- Direct usage of `mlx-vlm` library
- VLM processing via `VLMProcessor` class
- Environment-based model configuration (`VISION_MODEL`)
- Custom exceptions (`VLMConfigurationError`, `VLMModelLoadError`, etc.)

**Integration Strategy**:

**Option A: Wrapper Adapter** (Chosen)
- Create `MLXAdapter` that wraps existing mlx-vlm functionality
- Provides OpenAI-compatible interface on top of MLX calls
- Maintains backward compatibility with existing code
- Allows gradual migration of image_processor to use llm_client

**Option B: Replace MLX Integration**
- Not chosen: Would break existing functionality
- Violates "must not break existing MLX integration" constraint

**Implementation Notes**:
- `MLXAdapter` translates OpenAI format → MLX format
- Maps image processing to chat completion format
- Preserves existing VLM configuration and error handling
- Add adapter incrementally without modifying image_processor initially
- Future: Migrate image_processor to use llm_client.MLXAdapter

---

## Decisions Summary

| Decision Area | Choice | Rationale |
|--------------|--------|-----------|
| **HTTP Client** | httpx | Async/sync support, minimal dependencies, flexible |
| **Caching** | In-memory dict with TTL | Simple, performant, no external storage needed |
| **Retry Logic** | Custom exponential backoff | Full control, minimal dependencies |
| **Fallback** | Configurable provider list | User control over resilience strategy |
| **API Format** | OpenAI /v1/chat/completions | Standard across LM Studio, Ollama, MLX wrapper |
| **MLX Integration** | Wrapper adapter | Maintains compatibility, enables gradual migration |

---

## Dependencies Confirmed

**Required**:
- `httpx>=0.27.0` - HTTP client with retry and async support

**Standard Library** (no installation):
- `json` - JSON parsing
- `typing` - Type hints
- `dataclasses` - Data models
- `threading` - Cache locking
- `time` - TTL management
- `enum` - Enumerations

**Optional** (for testing):
- Existing: `pytest`, `pytest-cov`

**Dependency Justification**:
- httpx: Only external dependency; provides async/sync HTTP with retries, widely adopted
- All other functionality uses standard library per minimal dependencies principle

---

## Next Steps → Phase 1

With research complete, proceed to Phase 1:
1. Define data models in `data-model.md`
2. Generate API contracts in `contracts/`
3. Create contract tests (will fail until implementation)
4. Write quickstart guide
5. Update CLAUDE.md with new module context
