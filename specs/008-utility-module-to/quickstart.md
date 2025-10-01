# Quickstart: LLM Utility Module

**Feature**: 008-utility-module-to
**Date**: 2025-09-30
**Status**: Reference Implementation Guide

## Overview

This quickstart demonstrates how to use the `llm_client` module to interact with local LLM services (Ollama, LM Studio) and MLX-optimized models.

---

## Installation

```bash
# Add httpx dependency to pyproject.toml
uv add httpx>=0.27.0

# Install in development mode
uv sync
```

---

## Basic Usage

### 1. Simple Generation (Ollama)

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

# Configure client for Ollama
config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434"
)

# Create client
client = LLMClient(config)

# Create request
request = LLMRequest(
    messages=[Message(role="user", content="What is 2+2?")]
)

# Generate response
response = client.generate(request)

print(f"Response: {response.content}")
print(f"Model: {response.model}")
print(f"Latency: {response.latency_ms}ms")
```

**Expected Output**:
```
Response: 2+2 equals 4.
Model: llama2
Latency: 245.6ms
```

---

### 2. Conversation with System Prompt

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

# Multi-turn conversation
request = LLMRequest(
    messages=[
        Message(role="system", content="You are a helpful math tutor."),
        Message(role="user", content="Explain why 2+2=4"),
    ],
    temperature=0.7,
    max_tokens=200
)

response = client.generate(request)
print(response.content)
```

---

### 3. List Available Models

```python
from llm_client import LLMClient, LLMConfig

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    cache_ttl=300  # Cache for 5 minutes
)
client = LLMClient(config)

# List models (first call fetches from API)
models = client.list_models()

for model in models:
    print(f"- {model.id} (provider: {model.provider})")
    if model.context_length:
        print(f"  Context length: {model.context_length}")

# Second call uses cache (faster)
models_cached = client.list_models()
```

**Expected Output**:
```
- llama2 (provider: ollama)
  Context length: 4096
- codellama (provider: ollama)
  Context length: 16384
```

---

### 4. Error Handling

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message
from llm_client.exceptions import (
    ConnectionError,
    TimeoutError,
    ValidationError
)

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    timeout=10.0
)
client = LLMClient(config)

try:
    request = LLMRequest(
        messages=[Message(role="user", content="Hello")]
    )
    response = client.generate(request)
    print(response.content)

except ConnectionError as e:
    print(f"Service unreachable: {e.message}")

except TimeoutError as e:
    print(f"Request timed out: {e.message}")

except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

---

### 5. Retry Configuration

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    max_retries=3,              # Retry up to 3 times
    retry_delay=1.0,            # Start with 1s delay
    retry_max_delay=10.0,       # Cap at 10s
    retry_exponential_base=2.0  # Double delay each retry
)

client = LLMClient(config)

request = LLMRequest(
    messages=[Message(role="user", content="Hello")]
)

response = client.generate(request)

# Check if retries occurred
if response.retry_count > 0:
    print(f"Succeeded after {response.retry_count} retries")
```

---

### 6. Fallback Providers

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

# Primary: Ollama
# Fallback 1: LM Studio
# Fallback 2: MLX
fallback1 = LLMConfig(provider="lmstudio", base_url="http://localhost:1234")
fallback2 = LLMConfig(provider="mlx", base_url="local")

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    max_retries=2,
    fallback_configs=[fallback1, fallback2]
)

client = LLMClient(config)

request = LLMRequest(
    messages=[Message(role="user", content="Hello")]
)

response = client.generate(request)

# Check which provider was used
print(f"Provider: {response.provider}")
if response.used_fallback:
    print(f"Used fallback: {response.fallback_provider}")
```

**Expected Output** (if Ollama is down):
```
Provider: lmstudio
Used fallback: lmstudio
```

---

### 7. LM Studio with Authentication

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

config = LLMConfig(
    provider="lmstudio",
    base_url="http://localhost:1234",
    api_key="your-api-key-here"  # Optional for LM Studio
)

client = LLMClient(config)

request = LLMRequest(
    messages=[Message(role="user", content="Hello")],
    model="TheBloke/Llama-2-7B-GGUF"  # Specific model
)

response = client.generate(request)
print(response.content)
```

---

### 8. MLX Adapter (Image Processing)

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message
import os

# Set MLX model via environment variable (maintains compatibility)
os.environ['VISION_MODEL'] = 'google/gemma-3-4b'

config = LLMConfig(
    provider="mlx",
    base_url="local"  # MLX runs locally
)

client = LLMClient(config)

# MLX adapter translates to image processing
request = LLMRequest(
    messages=[Message(role="user", content="Describe the image at path/to/image.jpg")]
)

response = client.generate(request)
print(response.content)
```

---

### 9. Usage Statistics

```python
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

request = LLMRequest(
    messages=[Message(role="user", content="Count to 10")]
)

response = client.generate(request)

# Access usage statistics
if response.usage:
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")

print(f"Latency: {response.latency_ms}ms")
```

---

### 10. Cache Management

```python
from llm_client import LLMClient, LLMConfig

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    cache_ttl=60  # 1 minute cache
)
client = LLMClient(config)

# Populate cache
models = client.list_models()
print(f"Found {len(models)} models")

# Force refresh (invalidate cache)
client.invalidate_cache()

# Next call fetches fresh
models = client.list_models()
print(f"Refreshed: {len(models)} models")
```

---

## Integration with Existing Modules

### PDF Extractor Integration

```python
# In pdf_extractor module
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

def enhance_extracted_text(text: str) -> str:
    """Enhance extracted PDF text using LLM."""

    config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
    client = LLMClient(config)

    request = LLMRequest(
        messages=[
            Message(role="system", content="Clean and format extracted PDF text."),
            Message(role="user", content=f"Clean this text: {text}")
        ]
    )

    response = client.generate(request)
    return response.content
```

### Image Processor Integration

```python
# Gradual migration example
from llm_client import LLMClient, LLMConfig
from llm_client.adapters.mlx import MLXAdapter

def process_image_with_llm_client(image_path: str) -> str:
    """Process image using llm_client MLX adapter."""

    config = LLMConfig(provider="mlx", base_url="local")
    client = LLMClient(config)

    # Use existing MLX VLM functionality through adapter
    request = LLMRequest(
        messages=[Message(role="user", content=f"Describe: {image_path}")]
    )

    response = client.generate(request)
    return response.content
```

### Audio Processor Integration

```python
# In audio_processor module
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

def summarize_transcription(transcript: str) -> str:
    """Summarize audio transcription using LLM."""

    config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
    client = LLMClient(config)

    request = LLMRequest(
        messages=[
            Message(role="system", content="Summarize transcripts concisely."),
            Message(role="user", content=transcript)
        ]
    )

    response = client.generate(request)
    return response.content
```

---

## CLI Usage (Future)

```bash
# List models
uv run python -m llm_client list-models --provider ollama

# Generate completion
uv run python -m llm_client generate --provider ollama --message "Hello world"

# With specific model
uv run python -m llm_client generate --provider ollama --model llama2 --message "What is AI?"
```

---

## Testing Your Setup

Run this script to verify your setup:

```python
# test_llm_setup.py
from llm_client import LLMClient, LLMConfig, LLMRequest, Message

def test_setup():
    """Test LLM client setup."""

    providers_to_test = [
        ("ollama", "http://localhost:11434"),
        ("lmstudio", "http://localhost:1234"),
    ]

    for provider, base_url in providers_to_test:
        print(f"\nTesting {provider}...")

        try:
            config = LLMConfig(provider=provider, base_url=base_url, timeout=5.0)
            client = LLMClient(config)

            # Test model listing
            models = client.list_models()
            print(f"✓ Found {len(models)} models")

            # Test generation
            request = LLMRequest(
                messages=[Message(role="user", content="Say 'test'")]
            )
            response = client.generate(request)
            print(f"✓ Generation works: {response.content[:50]}...")

        except Exception as e:
            print(f"✗ Failed: {e}")

if __name__ == "__main__":
    test_setup()
```

Run with:
```bash
uv run python test_llm_setup.py
```

---

## Next Steps

1. Start Ollama or LM Studio locally
2. Run the quickstart examples
3. Integrate with your processing modules
4. Run contract tests: `uv run pytest tests/contract/ -v`
5. Check the generated documentation for API reference

---

## Troubleshooting

**"ConnectionError: Service unreachable"**
- Verify Ollama/LM Studio is running
- Check the base_url is correct
- Test with: `curl http://localhost:11434/api/tags` (Ollama)

**"No models available"**
- Pull models in Ollama: `ollama pull llama2`
- Check LM Studio has models downloaded

**"ValidationError: Invalid provider"**
- Provider must be one of: "ollama", "lmstudio", "mlx"
- Check for typos in provider name

**"TimeoutError: Request timed out"**
- Increase timeout in config
- Check service is responding
- Try with smaller model

---

**Status**: Ready for implementation → Run `/tasks` to generate implementation tasks
