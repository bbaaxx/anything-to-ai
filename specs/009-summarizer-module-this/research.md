# Research: Text Summarizer Module

**Created**: 2025-10-01
**Phase**: 0 - Outline & Research
**Purpose**: Resolve technical unknowns and establish implementation patterns

## Research Topics

### 1. LLM Prompt Engineering for Summarization

**Decision**: Use structured prompts with explicit instructions for summary length, tag generation, and language handling

**Rationale**:
- Modern LLMs perform better with clear, structured instructions
- Explicit tag count requirements (minimum 3) ensure consistency
- Language instructions ("always respond in English") improve reliability
- Content density analysis can be delegated to the LLM with appropriate prompting

**Alternatives Considered**:
- Fine-tuned summarization models: Rejected due to complexity and maintenance overhead
- Rule-based summarization: Rejected due to poor quality and lack of multilingual support
- Hybrid approach (rules + LLM): Rejected for initial implementation (can add later)

**Implementation Guidance**:
```python
# Prompt structure:
# 1. Role definition ("You are a text summarization expert")
# 2. Task description (summarize text, generate tags)
# 3. Constraints (minimum 3 tags, English output, smart length)
# 4. Format specification (JSON structure)
# 5. Content to summarize
```

### 2. Text Chunking Strategy for Large Documents

**Decision**: Sliding window approach with 10,000 word chunks, 500 word overlap, hierarchical summarization

**Rationale**:
- 10,000 word chunks fit comfortably within LLM context windows
- Overlap preserves context across chunk boundaries
- Hierarchical summarization (summarize chunks, then summarize summaries) maintains coherence
- Token-efficient: only processes what's necessary

**Alternatives Considered**:
- Fixed-size chunks without overlap: Rejected due to context loss at boundaries
- Semantic chunking (by paragraphs/sections): Deferred to future iteration (adds complexity)
- Map-reduce pattern: Considered equivalent to hierarchical approach for this use case

**Implementation Guidance**:
```python
def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

# For hierarchical summarization:
# 1. Summarize each chunk independently
# 2. Combine chunk summaries
# 3. If combined summaries > 10k words, recursively summarize
# 4. Generate final tags from final summary
```

### 3. Language Detection Approach

**Decision**: Rely on LLM language detection capabilities via prompt instructions

**Rationale**:
- Modern LLMs can detect and translate automatically
- No additional dependencies required (aligns with minimal dependencies principle)
- Prompt instruction "detect the language and always respond in English" is sufficient
- Reduces code complexity significantly

**Alternatives Considered**:
- langdetect library: Rejected (adds dependency, LLM can handle this)
- polyglot library: Rejected (heavy dependency, not needed)
- Manual language detection: Rejected (reinventing the wheel)

**Implementation Guidance**:
```python
# Include in prompt:
# "The input text may be in any language. Detect the language and provide
#  your summary and tags in English regardless of the input language."
```

### 4. Output Format Design

**Decision**: JSON as primary format with strict schema, plain text as optional human-readable format

**Rationale**:
- JSON enables programmatic consumption by other modules
- Strict schema (defined via Pydantic models) ensures consistency
- Plain text format for human readability and direct CLI use
- Format selection via CLI flag (--format json|plain)

**JSON Schema**:
```json
{
  "summary": "string - the generated summary",
  "tags": ["string", "string", "string", "..."],
  "metadata": {
    "input_length": "integer - word count",
    "chunked": "boolean - whether chunking was used",
    "detected_language": "string - optional",
    "processing_time": "float - seconds"
  }
}
```

**Plain Text Format**:
```
SUMMARY:
<summary text>

TAGS:
- tag1
- tag2
- tag3

METADATA:
Input length: 1234 words
Chunked: No
Processing time: 2.34s
```

**Implementation Guidance**:
- Use Pydantic models for JSON schema validation
- Implement formatters as separate functions (JSON formatter, plain text formatter)
- Keep formatters under 50 lines each

### 5. Error Handling Strategy

**Decision**: Explicit error types for different failure modes, graceful degradation where possible

**Rationale**:
- Clear error messages improve debugging and user experience
- Typed exceptions enable proper error handling by callers
- Graceful degradation (e.g., continue with fewer tags if LLM struggles) improves reliability

**Error Types**:
```python
class SummarizerError(Exception):
    """Base exception for summarizer module"""

class InvalidInputError(SummarizerError):
    """Raised for invalid input (empty, non-UTF-8, etc.)"""

class LLMError(SummarizerError):
    """Raised when LLM client fails"""

class ValidationError(SummarizerError):
    """Raised when output validation fails (e.g., <3 tags)"""
```

**Alternatives Considered**:
- Generic exceptions: Rejected (loses type information)
- No custom exceptions: Rejected (harder to handle specific cases)

### 6. Integration with Existing LLM Client Module

**Decision**: Use llm_client module via its public API, wrap in adapter if needed

**Rationale**:
- llm_client module already exists and is tested
- Provides OpenAI-compatible interface
- Adapter pattern allows future client swapping
- Maintains separation of concerns

**Implementation Guidance**:
```python
# Import from llm_client
from llm_client import create_client, ChatMessage

# Wrapper for summarization-specific logic
class SummarizerLLMAdapter:
    def __init__(self, client):
        self.client = client

    def summarize(self, text: str, format_json: bool = True) -> Dict:
        """Summarize text using LLM"""
        prompt = self._build_prompt(text, format_json)
        response = self.client.chat_completion([
            ChatMessage(role="system", content=prompt)
        ])
        return self._parse_response(response)
```

### 7. CLI Interface Design

**Decision**: Follow existing module patterns (audio_processor, image_processor) for consistency

**Rationale**:
- Consistent CLI experience across all modules
- Users familiar with other modules can use this one immediately
- Enables easy piping between modules

**CLI Flags**:
```bash
python -m text_summarizer [options] <input_file_or_text>

Options:
  --format {json,plain}     Output format (default: json)
  --output FILE             Write output to file instead of stdout
  --verbose                 Enable verbose logging
  --stdin                   Read from stdin instead of file
```

**Usage Examples**:
```bash
# Direct text
echo "Long text..." | python -m text_summarizer --stdin

# From file
python -m text_summarizer document.txt

# Pipe from another module
python -m pdf_extractor doc.pdf | python -m text_summarizer --stdin --format plain

# Output to file
python -m text_summarizer article.txt --output summary.json
```

## Research Summary

All technical decisions have been made with the following priorities:

1. **Constitutional Compliance**: All files will stay under 250 lines, composition-first design
2. **Minimal Dependencies**: Only llm_client + standard library
3. **Consistency**: Follows existing module patterns in the codebase
4. **Testability**: Clear interfaces enable comprehensive testing
5. **Simplicity**: Delegate complex logic (language detection, smart summarization) to LLM

## Next Phase

Phase 1 will use these research findings to:
1. Define data models (Pydantic classes)
2. Create API contracts (function signatures)
3. Generate contract tests
4. Write quickstart guide
5. Update CLAUDE.md

---

**Status**: ✅ Complete
**Artifacts**: Research decisions documented, ready for Phase 1
