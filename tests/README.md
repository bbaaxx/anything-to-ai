# Tests

This directory contains comprehensive test suites for the makeme-a-podcast-from-docs project.

## Test Structure

```
tests/
├── contract/          # Contract tests (API compliance)
├── integration/       # Integration tests (end-to-end workflows)
├── unit/             # Unit tests (individual components)
└── human_review_quick_test  # Human review test script
```

## Test Categories

### Contract Tests (`contract/`)

Verify that modules implement their APIs correctly and maintain backward compatibility.

### Integration Tests (`integration/`)

Test complete workflows across multiple modules, including:

- End-to-end processing pipelines
- Error handling and recovery
- Model compatibility and fallbacks
- Performance under load

### Unit Tests (`unit/`)

Test individual components in isolation, including:

- Algorithm correctness
- Edge case handling
- Input validation
- Performance characteristics

## Human Review Test Script

The `human_review_quick_test` script provides a comprehensive, human-readable test of all major functionality:

### Features

- **Bash-only implementation** - No Python dependencies
- **Sample data integration** - Uses files from `sample-data/` directory
- **Graceful error handling** - Continues testing even if some modules fail
- **Detailed logging** - Colored output with comprehensive results
- **Auto-configuration** - Sets up VLM models and other dependencies automatically

### Usage

```bash
# Run complete test suite
./tests/human_review_quick_test

# View detailed results
cat ./tmp/human_test_*.log

# Clean up temporary files
rm -f ./tmp/human_test_*.log ./tmp/*_test.*
```

### What It Tests

1. **Audio Processor Module**

   - Audio transcription with multiple formats (plain, JSON, markdown)
   - Multiple audio files (podcast.mp3, silence.mp3)
   - Error handling for invalid files

2. **Image Processor Module**

   - Image description generation
   - Multiple output styles (brief, detailed)
   - JSON and plain text outputs
   - Batch processing capabilities

3. **PDF Extractor Module**

   - PDF metadata extraction
   - Text extraction with streaming
   - Plain text and structured outputs

4. **Text Summarizer Module**

   - Text summarization with LLM models
   - Tag generation and categorization
   - JSON and plain text outputs
   - Large document chunking

5. **Module Integration**
   - End-to-end pipelines (PDF → Extract → Summarize)
   - Cross-module data flow
   - Error propagation and handling

### Configuration

The script automatically configures:

- **VISION_MODEL** for image processing (defaults to `mlx-community/gemma-3-4b-it-4bit`)
- **LLM models** for text summarization (uses available local models)
- **Temporary directories** and file cleanup
- **Progress tracking** and verbose output

### Exit Codes

- **0**: All tests passed successfully
- **1**: One or more critical tests failed
- **Non-zero**: Script execution error

### Sample Output

```
=== Human Review Quick Test Suite ===
Starting comprehensive module testing...
Sample data directory: sample-data
Test log: ./tmp/human_test_1759489475.log

Testing Audio Processor Module
----------------------------------------
[✓] Audio transcription (podcast.mp3) PASSED
[✓] Audio transcription with markdown output PASSED
[✓] Audio transcription with JSON output PASSED

Testing Image Processor Module
----------------------------------------
[INFO] Setting VISION_MODEL to: mlx-community/gemma-3-4b-it-4bit
[✓] Image description (single image) PASSED
[✓] Image description with detailed style PASSED

...

=== Test Summary ===
All tests completed!
[✓] Human review test suite finished successfully
```

## Running Tests

### All Tests

```bash
# Run all test suites
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/contract/
```

### Individual Test Files

```bash
# Run specific test file
uv run pytest tests/unit/test_chunker.py

# Run with verbose output
uv run pytest tests/integration/test_workflows.py -v

# Run with coverage
uv run pytest --cov=.
```

## Test Data

Tests use sample data from the `sample-data/` directory:

- **Audio**: `podcast.mp3`, `silence.mp3`
- **Images**: Various JPEG and PNG files
- **PDFs**: Academic papers, articles, and documents with/without images

## Best Practices

1. **Run tests before committing** - Pre-commit hooks will catch many issues
2. **Use the human review script** - Quick sanity check of all major functionality
3. **Add tests for new features** - Maintain high test coverage
4. **Test edge cases** - Include error conditions and boundary cases
5. **Keep tests fast** - Unit tests should run quickly, integration tests can be slower
