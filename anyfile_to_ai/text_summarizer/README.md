# Text Summarizer Module

A Python module for summarizing text using LLM models with automatic language detection, intelligent chunking, and tag generation. Supports pipeline integration with other modules for end-to-end document processing.

## Installation & Setup

### Prerequisites

- Python 3.13 or higher
- Ollama (for LLM backend) or compatible OpenAI-style API
- UV package manager (recommended) or pip

### Dependencies Installation

Using UV (recommended):

```bash
uv sync  # Installs all project dependencies
```

Using pip:

```bash
pip install pydantic
```

### LLM Backend Setup

This module requires an LLM backend. The default configuration uses Ollama:

1. **Install Ollama**:

   ```bash
   # macOS
   brew install ollama

   # Or download from https://ollama.ai
   ```

2. **Start Ollama service**:

   ```bash
   ollama serve
   ```

3. **Pull a model** (in another terminal):
   ```bash
   ollama pull llama3.2
   # Or: ollama pull llama2, mistral, etc.
   ```

### Verify Installation

```bash
python -m text_summarizer --help
```

## CLI Usage

### Basic Text Summarization

```bash
# Summarize a text file (JSON output)
python -m text_summarizer document.txt

# Summarize with plain text output
python -m text_summarizer document.txt --format plain

# Summarize from stdin
echo "Your text here..." | python -m text_summarizer --stdin

# Save to file
python -m text_summarizer document.txt --output summary.json
```

### Output Formats

**JSON Output (default)**:

```bash
python -m text_summarizer article.txt
```

Returns:

```json
{
  "summary": "A concise summary of the content...",
  "tags": ["tag1", "tag2", "tag3"],
  "metadata": {
    "input_length": 1234,
    "chunked": false,
    "chunk_count": null,
    "detected_language": "en",
    "processing_time": 2.34
  }
}
```

**Plain Text Output**:

```bash
python -m text_summarizer article.txt --format plain
```

Returns:

```
SUMMARY:
A concise summary of the content...

TAGS:
- tag1
- tag2
- tag3

METADATA:
Input length: 1234 words
Chunked: No
Processing time: 2.34s
```

### Model Selection

```bash
# Use a specific model
python -m text_summarizer document.txt --model llama2

# Use Mistral model
python -m text_summarizer document.txt --model mistral:latest

# Use a larger model for better quality
python -m text_summarizer document.txt --model llama3:70b
```

### Provider Selection

```bash
# Use Ollama (default)
python -m text_summarizer document.txt --provider ollama

# Use LM Studio
python -m text_summarizer document.txt --provider lmstudio --model mistral

# Use MLX (local models on Apple Silicon)
python -m text_summarizer document.txt --provider mlx --model mlx-community/llama-3

# Combine provider and model
python -m text_summarizer document.txt --provider lmstudio --model llama2 --format plain
```

### Advanced Options

```bash
# Exclude metadata from output
python -m text_summarizer document.txt --no-metadata

# Verbose mode with progress information
python -m text_summarizer document.txt --verbose

# Combine options with custom model
python -m text_summarizer document.txt --format plain --model mistral --output summary.txt --verbose
```

## Pipeline Integration

The text_summarizer integrates seamlessly with other modules:

### PDF → Summarizer Pipeline

```bash
# Extract text from PDF and summarize
python -m pdf_extractor document.pdf | python -m text_summarizer --stdin
```

### Audio → Summarizer Pipeline

```bash
# Transcribe audio and summarize the transcript
python -m audio_processor podcast.mp3 --format plain | python -m text_summarizer --stdin
```

### Image → Summarizer Pipeline

```bash
# Extract text from image and summarize
python -m image_processor screenshot.png --format plain | python -m text_summarizer --stdin
```

### Multi-stage Pipeline

```bash
# Process PDF with images, then summarize
python -m pdf_extractor document.pdf --format plain | python -m text_summarizer --stdin --format plain > summary.txt
```

## Python API

### Basic Usage

```python
from text_summarizer import summarize_text

# Simple summarization
text = "Your long text here..."
result = summarize_text(text)

print(f"Summary: {result.summary}")
print(f"Tags: {', '.join(result.tags)}")
print(f"Language: {result.metadata.detected_language}")
```

### Progress Tracking

The text_summarizer now supports the unified progress tracking system:

```python
from text_summarizer import create_summarizer
from progress_tracker import ProgressEmitter, CLIProgressConsumer

# Create progress emitter
emitter = ProgressEmitter(total=None, label="Summarizing text")
emitter.add_consumer(CLIProgressConsumer())

# Create summarizer and process with progress
summarizer = create_summarizer()
result = summarizer.summarize(text, progress_emitter=emitter)

# For chunked text, progress shows each chunk being processed:
# Summarizing text |████████░░░░░░░░| 60% (6/10 chunks)
```

### Advanced Usage

```python
from text_summarizer import create_summarizer, summarize_text, SummaryResult
from llm_client import LLMClient, LLMConfig, Provider
from progress_tracker import ProgressEmitter, CLIProgressConsumer

# Use a different model and provider
result = summarize_text(text, model="mistral:latest", provider="ollama")

# Use LM Studio
result = summarize_text(text, model="llama2", provider="lmstudio")

# Create custom summarizer with specific model, provider, and configuration
config = LLMConfig(
    provider=Provider.OLLAMA.value,
    base_url="http://localhost:11434"
)
client = LLMClient(config)

summarizer = create_summarizer(
    llm_client=client,
    chunk_size=5000,    # Words per chunk
    chunk_overlap=200,  # Overlap between chunks
    model="llama3:70b",  # Use a larger model
    provider="ollama"   # Specify provider
)

# Summarize with custom settings and progress tracking
emitter = ProgressEmitter(total=None, label="Processing")
emitter.add_consumer(CLIProgressConsumer())

result = summarizer.summarize(
    text,
    include_metadata=True,
    progress_emitter=emitter
)

# Access detailed metadata
if result.metadata:
    print(f"Processed {result.metadata.input_length} words")
    if result.metadata.chunked:
        print(f"Used {result.metadata.chunk_count} chunks")
    print(f"Processing time: {result.metadata.processing_time:.2f}s")
```

### Text Chunking

```python
from text_summarizer import chunk_text

# Split large text into chunks
text = "Very long text..." * 10000
chunks = chunk_text(text, chunk_size=10000, overlap=500)

for chunk in chunks:
    print(f"Chunk {chunk.index}: words {chunk.start_word}-{chunk.end_word}")
    print(f"Content length: {len(chunk.content)} chars")
```

## Features

### Intelligent Summarization

- **Adaptive length**: LLM determines appropriate summary length based on content density
- **Quality tags**: Minimum 3 categorization tags per summary
- **Context preservation**: Maintains key information and relationships

### Language Support

- **Auto-detection**: Automatically detects input language
- **English output**: Always returns summaries and tags in English
- **Multilingual input**: Supports any language the LLM model can process

### Large Document Handling

- **Automatic chunking**: Texts >10,000 words are automatically chunked
- **Hierarchical summarization**: Summaries of chunks are combined intelligently
- **Sliding window**: Configurable overlap prevents context loss at boundaries
- **Recursive processing**: Handles arbitrarily large documents

### Error Handling

- **Exit code 0**: Success
- **Exit code 1**: Invalid input (empty text, bad encoding, file not found)
- **Exit code 2**: LLM error (API failure, timeout, model not found)
- **Exit code 3**: Validation error (insufficient tags, invalid output)

## API Reference

### Functions

#### `summarize_text(text, *, include_metadata=True, model="llama3.2:latest", provider="ollama")`

Main function for text summarization.

**Parameters:**

- `text` (str): Input text to summarize
- `include_metadata` (bool): Include processing metadata (default: True)
- `model` (str): Model name to use (default: "llama3.2:latest")
- `provider` (str): Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

**Returns:**

- `SummaryResult`: Object with summary, tags, and optional metadata

**Raises:**

- `InvalidInputError`: If text is empty or invalid
- `LLMError`: If LLM processing fails
- `ValidationError`: If output doesn't meet requirements

#### `create_summarizer(llm_client=None, *, chunk_size=10000, chunk_overlap=500, model="llama3.2:latest", provider="ollama")`

Factory function to create a summarizer instance.

**Parameters:**

- `llm_client`: Optional custom LLM client (uses default if None)
- `chunk_size` (int): Words per chunk for large texts (default: 10000)
- `chunk_overlap` (int): Overlap words between chunks (default: 500)
- `model` (str): Model name to use (default: "llama3.2:latest")
- `provider` (str): Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

**Returns:**

- `TextSummarizer`: Configured summarizer instance

#### `chunk_text(text, chunk_size=10000, overlap=500)`

Utility function to split text into overlapping chunks.

**Parameters:**

- `text` (str): Text to chunk
- `chunk_size` (int): Target words per chunk
- `overlap` (int): Overlap words between chunks

**Returns:**

- `List[TextChunk]`: List of text chunks with metadata

### Data Models

#### `SummaryResult`

- `summary` (str): Generated summary text
- `tags` (List[str]): Categorization tags (minimum 3)
- `metadata` (Optional[SummaryMetadata]): Processing metadata

#### `SummaryMetadata`

- `input_length` (int): Word count of input
- `chunked` (bool): Whether chunking was used
- `chunk_count` (Optional[int]): Number of chunks if chunked
- `detected_language` (Optional[str]): ISO language code
- `processing_time` (float): Processing time in seconds

#### `TextChunk`

- `index` (int): Sequential chunk index (0-based)
- `content` (str): Chunk text content
- `start_word` (int): Starting word position
- `end_word` (int): Ending word position

## Configuration

### Custom LLM Backend

To use a different LLM backend:

```python
from text_summarizer import create_summarizer, summarize_text
from llm_client import LLMClient, LLMConfig, Provider

# Simple way: use provider parameter
result = summarize_text(text, provider="lmstudio", model="mistral")

# Advanced: configure custom client
config = LLMConfig(
    provider=Provider.LMSTUDIO.value,
    base_url="http://localhost:1234"
)
client = LLMClient(config)
summarizer = create_summarizer(llm_client=client, model="mistral")
```

### Available Providers

- **ollama** (default): Ollama running on `http://localhost:11434`
- **lmstudio**: LM Studio running on `http://localhost:1234`
- **mlx**: MLX local models (Apple Silicon only)

### Custom Prompt Template

The summarization prompt can be customized by editing `text_summarizer/prompt_template.txt`:

```bash
# Edit the prompt template
vim text_summarizer/prompt_template.txt
# or
nano text_summarizer/prompt_template.txt
```

The template uses two placeholders:

- `{instruction}` - Replaced with task-specific instruction
- `{text}` - Replaced with the actual text to summarize

**Example customization:**

```text
You are an expert analyst. {instruction}

Be concise and focus on key insights.

Output format:
{{
    "summary": "brief summary",
    "tags": ["tag1", "tag2", "tag3"],
    "language": "en"
}}

Text: {text}
```

Changes take effect when the module is reloaded (restart Python process or application).

### Chunking Strategy

For very large documents, adjust chunking parameters:

```python
# Smaller chunks for faster processing
summarizer = create_summarizer(chunk_size=5000, chunk_overlap=250)

# Larger chunks for better context
summarizer = create_summarizer(chunk_size=20000, chunk_overlap=1000)
```

## Performance Characteristics

### Expected Performance

- **Small text** (<1k words): < 5 seconds
- **Medium text** (1k-10k words): < 30 seconds
- **Large text** (10k-100k words): < 5 minutes
- **Memory usage**: < 200MB typical

### Performance Tips

1. Use smaller models (e.g., `llama2` instead of `llama3`) for faster processing
2. Reduce chunk_size for quicker processing of very large documents
3. Use `--no-metadata` flag to skip metadata computation
4. Process multiple documents in parallel using shell tools

## Troubleshooting

### "model not found" error

```bash
# Pull the model
ollama pull llama3.2

# Or use a different model that's already available
python -m text_summarizer document.txt --model llama2

# Check which models are available
ollama list
```

### "connection refused" error

```bash
# For Ollama
ollama serve
curl http://localhost:11434/api/tags

# For LM Studio
# Start LM Studio and enable "Local Server" in settings
curl http://localhost:1234/v1/models

# Switch provider if one isn't working
python -m text_summarizer document.txt --provider lmstudio
```

### Insufficient tags error

The LLM must generate at least 3 tags. If this fails:

- Try a different/larger model
- Check that the input text has enough content
- Verify LLM service is responding correctly

### Empty or gibberish summaries

- Ensure the LLM model is properly loaded
- Try a more capable model (e.g., upgrade from `tiny` to `small`)
- Check input text is valid UTF-8

## Examples

### Example 1: Summarize Research Paper

```bash
# Use default model
python -m text_summarizer research_paper.txt --format plain --verbose

# Use a larger, more capable model for better quality
python -m text_summarizer research_paper.txt --model llama3:70b --format plain
```

### Example 2: Batch Processing

```bash
# Summarize all text files in a directory
for file in documents/*.txt; do
    echo "Processing $file..."
    python -m text_summarizer "$file" --output "summaries/$(basename "$file" .txt)_summary.json"
done
```

### Example 3: API Integration

```python
from text_summarizer import summarize_text
import sys

def process_document(filepath):
    """Process a document and return structured summary."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        result = summarize_text(text)

        return {
            'file': filepath,
            'summary': result.summary,
            'tags': result.tags,
            'word_count': result.metadata.input_length if result.metadata else None,
            'success': True
        }
    except Exception as e:
        return {
            'file': filepath,
            'error': str(e),
            'success': False
        }

# Use in application
doc = process_document('article.txt')
if doc['success']:
    print(f"Summary: {doc['summary']}")
    print(f"Tags: {', '.join(doc['tags'])}")
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/contract/test_summarizer_api.py -v
uv run pytest tests/unit/test_chunker.py -v
uv run pytest tests/unit/test_summarizer_models.py -v

# Run integration tests (requires LLM backend)
uv run pytest tests/integration/test_summarizer_workflow.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check text_summarizer/

# Check file lengths (must be <250 lines per constitution)
uv run python check_file_lengths.py
```

## Architecture

The module follows a composition-first design:

```
text_summarizer/
├── __init__.py          # Public API exports
├── __main__.py          # CLI entry point
├── models.py            # Pydantic data models
├── exceptions.py        # Custom exceptions
├── chunker.py           # Text chunking logic
├── llm_adapter.py       # LLM client integration
└── processor.py         # Core summarization logic
```

Each file is kept under 250 lines to maintain simplicity and composability.

## License

See project root LICENSE file.

## Contributing

This module is part of the anything-to-ai project. See the main project README and `specs/009-summarizer-module-this/` for development guidelines.
