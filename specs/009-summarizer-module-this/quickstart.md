# Quickstart: Text Summarizer Module

**Feature**: Text Summarizer
**Branch**: `009-summarizer-module-this`
**Purpose**: Verify the summarizer module works end-to-end

## Prerequisites

```bash
# Install dependencies (if not already installed)
uv sync

# Ensure LLM client module is available
python -c "import llm_client; print('✓ llm_client available')"
```

## Basic Usage

### 1. Summarize a Simple Text

```bash
# Create a test file
echo "Artificial intelligence has revolutionized many industries. Machine learning algorithms can now process vast amounts of data and identify patterns that humans might miss. Deep learning, a subset of machine learning, uses neural networks with multiple layers to learn complex representations. Natural language processing enables computers to understand and generate human language. Computer vision allows machines to interpret visual information from the world. These technologies are being applied in healthcare, finance, autonomous vehicles, and many other domains." > /tmp/test_ai.txt

# Summarize it
python -m text_summarizer /tmp/test_ai.txt

# Expected output (JSON format):
# {
#   "summary": "AI technologies including machine learning, deep learning, NLP, and computer vision are transforming industries like healthcare, finance, and autonomous vehicles by processing data and recognizing patterns.",
#   "tags": ["artificial intelligence", "machine learning", "technology applications"],
#   "metadata": {
#     "input_length": 68,
#     "chunked": false,
#     "chunk_count": null,
#     "detected_language": "en",
#     "processing_time": 1.23
#   }
# }
```

**Validation**:
- ✓ Returns valid JSON
- ✓ Summary is non-empty and concise
- ✓ At least 3 tags present
- ✓ Metadata shows input_length = 68 words
- ✓ chunked = false (text is small)

### 2. Plain Text Output Format

```bash
python -m text_summarizer /tmp/test_ai.txt --format plain

# Expected output:
# SUMMARY:
# AI technologies including machine learning, deep learning, NLP, and
# computer vision are transforming industries like healthcare, finance,
# and autonomous vehicles by processing data and recognizing patterns.
#
# TAGS:
# - artificial intelligence
# - machine learning
# - technology applications
#
# METADATA:
# Input length: 68 words
# Chunked: No
# Processing time: 1.23s
```

**Validation**:
- ✓ Human-readable format
- ✓ Clear section headers
- ✓ Tags as bullet list

### 3. Read from Stdin

```bash
echo "Climate change is one of the most pressing challenges facing humanity. Rising global temperatures are causing more frequent extreme weather events. Sea levels are rising due to melting polar ice caps. Scientists agree that human activities, particularly the burning of fossil fuels, are the primary drivers. Renewable energy sources like solar and wind power offer potential solutions." | python -m text_summarizer --stdin --format plain

# Expected output:
# SUMMARY:
# Climate change, driven primarily by fossil fuel consumption, causes
# rising temperatures, extreme weather, and sea level rise, with renewable
# energy as a key solution.
#
# TAGS:
# - climate change
# - environmental issues
# - renewable energy
```

**Validation**:
- ✓ Reads from stdin correctly
- ✓ Processes and summarizes
- ✓ Returns appropriate tags

### 4. Large Text with Chunking

```bash
# Generate a large text file (simulate with repeated content)
python -c "
text = '''The history of computing spans many decades and involves countless innovations.
From the early mechanical calculators to modern quantum computers, each era has brought
significant advancements. The invention of the transistor revolutionized electronics.
The development of programming languages made computers more accessible. The internet
connected billions of devices worldwide. Mobile computing put powerful computers in
everyone's pocket. Cloud computing enabled massive scalability. Artificial intelligence
is now pushing the boundaries of what's possible.
'''
# Repeat to exceed 10,000 words
large_text = (text + ' ') * 2000
with open('/tmp/large_text.txt', 'w') as f:
    f.write(large_text)
print(f'Created file with ~{len(large_text.split())} words')
"

# Summarize large text
python -m text_summarizer /tmp/large_text.txt

# Expected output includes:
# {
#   ...
#   "metadata": {
#     "input_length": ~16000,
#     "chunked": true,
#     "chunk_count": 2,
#     ...
#   }
# }
```

**Validation**:
- ✓ Handles large text (>10k words)
- ✓ metadata.chunked = true
- ✓ metadata.chunk_count > 1
- ✓ Still generates coherent summary
- ✓ Still generates at least 3 tags

### 5. Non-English Text (Multilingual)

```bash
# Spanish text
echo "La inteligencia artificial está transformando el mundo. Los algoritmos de aprendizaje automático pueden procesar grandes cantidades de datos. Esta tecnología se aplica en medicina, finanzas y transporte." | python -m text_summarizer --stdin --format plain

# Expected output (in English):
# SUMMARY:
# Artificial intelligence is transforming the world through machine
# learning algorithms that process large amounts of data, with applications
# in medicine, finance, and transportation.
#
# TAGS:
# - artificial intelligence
# - machine learning
# - technology applications
```

**Validation**:
- ✓ Detects non-English input (Spanish)
- ✓ Outputs summary in English
- ✓ Tags are in English
- ✓ Preserves meaning from original

### 6. Output to File

```bash
python -m text_summarizer /tmp/test_ai.txt --output /tmp/summary.json

# Verify file created
cat /tmp/summary.json
# Should contain JSON output

# Verify it's valid JSON
python -c "import json; json.load(open('/tmp/summary.json')); print('✓ Valid JSON')"
```

**Validation**:
- ✓ Creates output file
- ✓ File contains valid JSON
- ✓ File content matches expected format

## Integration with Other Modules

### 7. PDF → Summarizer Pipeline

```bash
# Assuming pdf_extractor module exists
python -m pdf_extractor sample-data/test.pdf | python -m text_summarizer --stdin --format plain
```

**Validation**:
- ✓ Accepts piped input from pdf_extractor
- ✓ Processes extracted text
- ✓ Returns summary and tags

### 8. Audio → Summarizer Pipeline

```bash
# Assuming audio_processor module exists
python -m audio_processor sample-data/audio.mp3 --format plain | python -m text_summarizer --stdin
```

**Validation**:
- ✓ Accepts piped input from audio_processor
- ✓ Processes transcribed text
- ✓ Returns JSON output

### 9. Image → Summarizer Pipeline

```bash
# Assuming image_processor module exists
python -m image_processor sample-data/image.jpg --format plain | python -m text_summarizer --stdin
```

**Validation**:
- ✓ Accepts piped input from image_processor
- ✓ Processes extracted text
- ✓ Returns summary

## Error Handling

### 10. Empty Input

```bash
echo "" | python -m text_summarizer --stdin
# Expected: Exit code 1, error message about empty input
```

**Validation**:
- ✓ Exits with code 1
- ✓ Shows clear error message

### 11. Invalid UTF-8

```bash
# Create file with invalid UTF-8 (binary data)
printf '\xFF\xFE Invalid UTF-8' > /tmp/invalid.txt
python -m text_summarizer /tmp/invalid.txt
# Expected: Exit code 1, error message about encoding
```

**Validation**:
- ✓ Detects invalid UTF-8
- ✓ Exits with code 1
- ✓ Shows encoding error message

### 12. File Not Found

```bash
python -m text_summarizer /nonexistent/file.txt
# Expected: Exit code 1, file not found error
```

**Validation**:
- ✓ Handles missing file gracefully
- ✓ Exits with code 1
- ✓ Shows clear error message

## Programmatic API Usage

### 13. Python API

```python
from text_summarizer import summarize_text

# Simple usage
text = """
Machine learning is a subset of artificial intelligence that enables
computers to learn from data without explicit programming. Deep learning
uses neural networks with multiple layers. Natural language processing
helps computers understand human language.
"""

result = summarize_text(text)
print(f"Summary: {result.summary}")
print(f"Tags: {', '.join(result.tags)}")
print(f"Word count: {result.metadata.input_length}")

# Expected output:
# Summary: Machine learning enables computers to learn from data using techniques like deep learning and natural language processing.
# Tags: machine learning, artificial intelligence, deep learning
# Word count: 34
```

**Validation**:
- ✓ Import works correctly
- ✓ Function returns SummaryResult
- ✓ Result has expected structure
- ✓ Metadata accessible

### 14. Custom LLM Client

```python
from text_summarizer import create_summarizer
from llm_client import create_client

# Create custom client (e.g., different model)
client = create_client(model="gpt-4")
summarizer = create_summarizer(llm_client=client)

result = summarizer.summarize("Some text here...")
print(result.summary)
```

**Validation**:
- ✓ Accepts custom LLM client
- ✓ Uses custom client for summarization
- ✓ Returns correct result

## Success Criteria

All tests above should:
- Execute without errors
- Return results matching expected formats
- Handle edge cases gracefully
- Provide clear error messages for failures
- Integrate seamlessly with existing modules

## Performance Validation

Expected performance benchmarks:
- Small text (<1k words): < 5 seconds
- Medium text (1k-10k words): < 30 seconds
- Large text (10k-100k words): < 5 minutes
- Memory usage: < 200MB for typical usage

---

**Status**: Ready for implementation
**Test Coverage**: Covers all functional requirements from spec.md
