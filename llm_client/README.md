# LLM Client Module

A unified Python client for accessing multiple local LLM service providers including Ollama, LM Studio, and MLX-optimized models. Features automatic provider fallback, retry logic, caching, and comprehensive error handling.

## Features

- **Unified Interface**: Single API for multiple LLM providers
- **Automatic Fallback**: Seamless fallback to alternative providers on failure
- **Retry Logic**: Exponential backoff retry mechanism with configurable delays
- **Model Caching**: In-memory caching of model listings with TTL expiration
- **Provider Support**: Ollama, LM Studio, and MLX-optimized models
- **Thread Safety**: Safe for concurrent operations
- **Comprehensive Error Handling**: Specific exception types for different error conditions

## Installation & Setup

### Prerequisites

- Python 3.13 or higher
- UV package manager (recommended) or pip
- Local LLM service (Ollama, LM Studio, or MLX runtime)

### Dependencies Installation

No external dependencies required - uses only standard library and httpx for HTTP requests.

### Provider Setup

#### Ollama Setup

```bash
# Install Ollama from https://ollama.com/
# Start Ollama service
ollama serve

# Pull a model (example)
ollama pull llama2:7b
```

#### LM Studio Setup

```bash
# Install LM Studio from https://lmstudio.ai/
# Start LM Studio and load a model via the UI
# Enable Local Server mode in LM Studio
```

#### MLX Setup

```bash
# MLX models are automatically managed
# No additional setup required for local models
```

### Verify Installation

```bash
python -m llm_client --help
```

## CLI Usage

### Basic LLM Generation

```bash
# Generate with default provider
python -m llm_client generate "What is the capital of France?"

# Specify provider and model
python -m llm_client generate --provider ollama --model llama2:7b "Explain quantum computing"

# List available models
python -m llm_client models --provider ollama
```

### Provider-Specific Commands

```bash
# Ollama operations
python -m llm_client generate --provider ollama --base-url http://localhost:11434 "Hello world"

# LM Studio operations
python -m llm_client generate --provider lmstudio --base-url http://localhost:1234 "Code review this function"

# Health check
python -m llm_client health --provider ollama
```

### Configuration File

```bash
# Use configuration file for complex setups
python -m llm_client generate --config llm_config.json "Complex query"
```

### CLI Options

- `--provider, -p`: LLM provider (`ollama`, `lmstudio`, `mlx`)
- `--base-url, -u`: Provider base URL (default varies by provider)
- `--model, -m`: Model name to use
- `--temperature, -t`: Sampling temperature (0.0-2.0)
- `--max-tokens`: Maximum tokens to generate
- `--timeout`: Request timeout in seconds
- `--config`: Path to configuration file
- `--verbose, -v`: Enable verbose output

## Python API Usage

### Basic Client Usage

```python
from llm_client import LLMClient, LLMConfig

# Simple configuration
config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434"
)

# Initialize client
client = LLMClient(config)

# Generate response
response = client.generate({
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "model": "llama2:7b",
    "temperature": 0.7
})

print(f"Response: {response.content}")
print(f"Model: {response.model}")
print(f"Latency: {response.latency_ms}ms")
```

### With Retry and Fallback

```python
from llm_client import LLMClient, LLMConfig

# Primary provider with fallback
primary_config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    max_retries=3,
    retry_delay=1.0
)

fallback_config = LLMConfig(
    provider="lmstudio",
    base_url="http://localhost:1234",
    max_retries=2
)

config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    max_retries=3,
    fallback_configs=[fallback_config]
)

client = LLMClient(config)
```

### Model Listing with Caching

```python
from llm_client import LLMClient, LLMConfig

config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

# List models (uses cache by default)
models = client.list_models()
for model in models:
    print(f"Model: {model.id}, Provider: {model.provider}")

# Invalidate cache to force refresh
client.invalidate_cache()

# Fetch fresh model list
models = client.list_models(use_cache=False)
```

### Advanced Configuration

```python
from llm_client import LLMClient, LLMConfig

# Comprehensive configuration
config = LLMConfig(
    provider="ollama",
    base_url="http://localhost:11434",
    timeout=60.0,
    max_retries=5,
    retry_delay=0.5,
    retry_max_delay=30.0,
    retry_exponential_base=2.0,
    cache_ttl=300,  # 5 minutes
    verify_ssl=True
)

client = LLMClient(config)
```

### Health Monitoring

```python
from llm_client import LLMClient, LLMConfig

config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

# Check provider health
if client.health_check():
    print("Provider is healthy")
else:
    print("Provider is not responding")
```

## Configuration Options

### LLMConfig Parameters

- **provider** (`str`): LLM provider name
  - `"ollama"`: Ollama service
  - `"lmstudio"`: LM Studio service
  - `"mlx"`: MLX-optimized local models
- **base_url** (`str`): Provider service URL
  - Ollama: `http://localhost:11434` (default)
  - LM Studio: `http://localhost:1234` (default)
  - MLX: Local model path or URL
- **api_key** (`str | None`): API key for authenticated providers (default: `None`)
- **timeout** (`float`): Request timeout in seconds (default: `30.0`)
- **verify_ssl** (`bool`): Verify SSL certificates (default: `True`)
- **max_retries** (`int`): Maximum retry attempts (default: `3`)
- **retry_delay** (`float`): Base delay between retries in seconds (default: `1.0`)
- **retry_max_delay** (`float`): Maximum delay between retries (default: `10.0`)
- **retry_exponential_base** (`float`): Exponential backoff base (default: `2.0`)
- **cache_ttl** (`int`): Model cache TTL in seconds (default: `300`)
- **fallback_configs** (`List[LLMConfig] | None`): Alternative provider configurations (default: `None`)

## Environment Setup

### Provider-Specific Environment Variables

```bash
# Ollama configuration
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TIMEOUT=60

# LM Studio configuration
export LMSTUDIO_BASE_URL=http://localhost:1234
export LMSTUDIO_API_KEY=your_key_here

# MLX configuration
export MLX_MODEL_PATH=/path/to/models
```

### Performance Optimization

```bash
# For faster HTTP requests
export LLM_CLIENT_TIMEOUT=30

# For aggressive retry behavior
export LLM_CLIENT_MAX_RETRIES=5
export LLM_CLIENT_RETRY_DELAY=0.5

# For longer model caching
export LLM_CLIENT_CACHE_TTL=600
```

## Error Handling

### Exception Types

```python
from llm_client.exceptions import (
    LLMError,
    ConfigurationError,
    ConnectionError,
    AuthenticationError,
    ModelNotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    GenerationError
)

try:
    response = client.generate(request)
except ConnectionError as e:
    print(f"Cannot connect to provider: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except ModelNotFoundError as e:
    print(f"Model not available: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except GenerationError as e:
    print(f"Generation failed: {e}")
```

### Common Issues & Solutions

**Connection Refused**:

```python
# Ensure provider service is running
# For Ollama: ollama serve
# For LM Studio: Start LM Studio with Local Server enabled
```

**Model Not Found**:

```python
# List available models first
models = client.list_models()
print("Available models:", [m.id for m in models])

# Use correct model name
response = client.generate({
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "llama2:7b"  # Use actual model name
})
```

**Timeout Errors**:

```python
# Increase timeout for slow models
config = LLMConfig(
    provider="ollama",
    timeout=120.0  # 2 minutes
)
```

**SSL Certificate Issues**:

```python
# Disable SSL verification for local services
config = LLMConfig(
    provider="ollama",
    verify_ssl=False
)
```

## Data Models

### Core Objects

```python
# Message in conversation
Message(role, content)

# LLM request
LLMRequest(
    messages, model=None, temperature=0.7,
    max_tokens=None, stream=False, request_id=None, timeout_override=None
)

# LLM response
LLMResponse(
    content, model, finish_reason, response_id, provider,
    latency_ms, usage=None, retry_count=0, used_fallback=False, fallback_provider=None
)

# Model information
ModelInfo(id, provider, object="model", created=None, owned_by=None, context_length=None, description=None)

# Token usage statistics
Usage(prompt_tokens, completion_tokens, total_tokens)

# Provider enumeration
Provider.OLLAMA, Provider.LMSTUDIO, Provider.MLX
```

## Examples with Integration

### With Audio Processor

```python
from llm_client import LLMClient, LLMConfig
from audio_processor import process_audio

# Transcribe audio and summarize with LLM
config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

audio_result = process_audio("sample-data/audio/podcast.mp3")
if audio_result.success:
    # Summarize transcript
    summary_request = {
        "messages": [
            {"role": "user", "content": f"Summarize this transcript: {audio_result.text}"}
        ],
        "model": "llama2:7b",
        "temperature": 0.3
    }
    summary = client.generate(summary_request)
    print(f"Summary: {summary.content}")
```

### With Image Processor

```python
from llm_client import LLMClient, LLMConfig
from image_processor import process_image

# Describe image and ask follow-up questions
config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

img_result = process_image("sample-data/images/DJI_20250817104854_0118_D.JPG")
if img_result.success:
    # Ask questions about the image
    qa_request = {
        "messages": [
            {"role": "user", "content": f"Based on this description: '{img_result.description}', what time of day was this photo taken?"}
        ],
        "model": "llama2:7b"
    }
    answer = client.generate(qa_request)
    print(f"Answer: {answer.content}")
```

### With PDF Extractor

```python
from llm_client import LLMClient, LLMConfig
from pdf_extractor import extract_text

# Extract PDF and generate podcast script
config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
client = LLMClient(config)

pdf_result = extract_text("sample-data/pdf/research_paper_no_images.pdf")
if pdf_result.success:
    # Generate podcast script
    script_request = {
        "messages": [
            {"role": "user", "content": f"Create a podcast script based on this research: {pdf_result.pages[0].text[:2000]}"}
        ],
        "model": "llama2:7b",
        "temperature": 0.7
    }
    script = client.generate(script_request)
    print(f"Podcast script: {script.content}")
```

## Provider-Specific Features

### Ollama Integration

- **OpenAI-Compatible API**: Uses `/v1/chat/completions` endpoint
- **Model Management**: Automatic model listing from `/v1/models`
- **Health Check**: Uses `/api/tags` endpoint for service validation
- **Streaming Support**: Ready for future streaming implementation

### LM Studio Integration

- **OpenAI-Compatible API**: Uses `/v1/chat/completions` endpoint
- **Model Discovery**: Automatic model listing
- **Authentication**: API key support for secure deployments
- **Custom Endpoints**: Configurable base URL for different deployments

### MLX Integration

- **Local Models**: Direct integration with MLX runtime
- **Optimized Performance**: Apple Silicon optimization
- **Model Path Support**: Flexible model loading from local paths
- **Minimal Dependencies**: No external service requirements

## Testing

```bash
# Run contract tests
PYTHONPATH=. uv run pytest tests/contract/test_llm_client*.py -v

# Test with mock providers
python -m llm_client generate --provider ollama "Test message"

# Integration tests
PYTHONPATH=. uv run pytest tests/integration/test_llm_integration.py -v
```

## Performance Notes

- **Caching**: Model listings cached for 5 minutes by default
- **Connection Pooling**: HTTP client reuses connections for efficiency
- **Timeout Handling**: Configurable timeouts prevent hanging requests
- **Memory Usage**: Minimal memory footprint with thread-safe operations
- **Concurrent Requests**: Safe for multiple simultaneous requests

## Limitations

- **Local Services Only**: Designed for local LLM services, not cloud providers
- **No Streaming**: Text generation only (streaming support planned)
- **Provider Dependency**: Requires running LLM service provider
- **Network Dependency**: HTTP-based communication with providers
- **Model Compatibility**: Depends on provider's supported model formats

## Integration Examples

### As Part of Document Processing Pipeline

```python
from llm_client import LLMClient, LLMConfig
from pdf_extractor import extract_text
from image_processor import process_image
from audio_processor import process_audio

# Unified processing pipeline
def process_document_with_llm(file_path):
    config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
    client = LLMClient(config)

    # Extract content based on file type
    if file_path.endswith('.pdf'):
        content = extract_text(file_path)
        content_type = "PDF document"
    elif file_path.endswith(('.jpg', '.png')):
        content = process_image(file_path)
        content_type = "Image description"
    elif file_path.endswith(('.mp3', '.wav')):
        content = process_audio(file_path)
        content_type = "Audio transcript"
    else:
        return "Unsupported file type"

    if content.success:
        # Generate summary using LLM
        summary_request = {
            "messages": [
                {"role": "user", "content": f"Summarize this {content_type}: {content.text or content.description}"}
            ],
            "model": "llama2:7b",
            "temperature": 0.3
        }
        summary = client.generate(summary_request)
        return summary.content

    return f"Failed to process {content_type}"
```

## Version

Current version: 0.1.0

## License

[Your License Here]
