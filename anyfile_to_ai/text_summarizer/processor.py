"""Core text summarization logic."""

import time
from pathlib import Path
from typing import Any

from .models import SummaryResult, SummaryMetadata
from .chunker import chunk_text
from .exceptions import InvalidInputError, ValidationError
from .llm_adapter import LLMAdapter, get_default_llm_client

# Load prompt template once at module level
_PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompt_template.txt"
_PROMPT_TEMPLATE = _PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")


class TextSummarizer:
    """Text summarizer that uses an LLM client."""

    def __init__(
        self,
        llm_client: Any | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        model: str = "llama3.2:latest",
        provider: str = "ollama",
    ):
        """
        Initialize TextSummarizer.

        Args:
            llm_client: Optional custom LLM client
            chunk_size: Words per chunk for large texts (auto-detected if None)
            chunk_overlap: Overlap words between chunks (auto-detected if None)
            model: Model name to use (default: "llama3.2:latest")
            provider: Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

        Raises:
            ValueError: If invalid parameters
        """
        client = llm_client or get_default_llm_client(model, provider)
        self.adapter = LLMAdapter(client, model)

        # Auto-detect appropriate chunk sizes based on model
        if chunk_size is None or chunk_overlap is None:
            chunk_size, chunk_overlap = self._get_model_chunk_params(model)

        if chunk_size <= 0:
            msg = "chunk_size must be positive"
            raise ValueError(msg)
        if chunk_overlap < 0:
            msg = "chunk_overlap must be non-negative"
            raise ValueError(msg)
        if chunk_size <= chunk_overlap:
            msg = "chunk_size must be greater than chunk_overlap"
            raise ValueError(msg)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _get_model_chunk_params(self, model: str) -> tuple[int, int]:
        """
        Get appropriate chunk size and overlap for a given model.

        Args:
            model: Model name

        Returns:
            Tuple of (chunk_size, chunk_overlap) in words
        """
        # Model-specific chunk sizes based on context window and capabilities
        model_lower = model.lower()

        # Small models need smaller chunks
        if any(name in model_lower for name in ["deepseek-r1:1.5b", "tiny", "small", "1.5b", "2b"]):
            return 2000, 200  # Small chunk size with small overlap

        # Medium models
        if any(name in model_lower for name in ["3b", "7b", "llama3.2", "mistral", "qwen"]):
            return 4000, 300  # Medium chunk size

        # Large models can handle bigger chunks
        if any(name in model_lower for name in ["8b", "13b", "30b", "70b", "llama3.1", "llama3"]):
            return 6000, 400  # Large chunk size

        # Default conservative settings
        return 3000, 250  # Conservative defaults

    def _build_prompt(self, text: str, is_chunk: bool = False) -> str:
        """Build prompt for LLM summarization using the template file."""
        instruction = "Summarize the following text chunk." if is_chunk else ("Summarize the following text and generate categorization tags.")

        # Format the prompt template with the instruction and text
        return _PROMPT_TEMPLATE.format(instruction=instruction, text=text)

    def summarize(self, text: str, include_metadata: bool = True, progress_emitter: Any | None = None) -> SummaryResult:
        """
        Summarize text.

        Args:
            text: Input text to summarize
            include_metadata: Whether to include metadata
            progress_emitter: Optional progress tracker

        Returns:
            SummaryResult with summary, tags, and optional metadata

        Raises:
            InvalidInputError: If text is invalid
            ValidationError: If result doesn't meet requirements
        """
        start_time = time.time()

        # Validate input
        if not text or not text.strip():
            msg = "Text must not be empty"
            raise InvalidInputError(msg)

        words = text.split()
        word_count = len(words)

        # Determine if chunking is needed
        needs_chunking = word_count > self.chunk_size

        if progress_emitter and needs_chunking:
            chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
            progress_emitter.update_total(len(chunks) + 1)

        if needs_chunking:
            result = self._summarize_chunked(text, word_count, progress_emitter)
        else:
            if progress_emitter:
                progress_emitter.update_total(1)
            result = self._summarize_direct(text)
            if progress_emitter:
                progress_emitter.update(1)

        if progress_emitter:
            progress_emitter.complete()

        # Add metadata
        if include_metadata:
            processing_time = time.time() - start_time
            metadata = SummaryMetadata(
                input_length=word_count,
                chunked=needs_chunking,
                chunk_count=len(chunk_text(text, self.chunk_size, self.chunk_overlap)) if needs_chunking else None,
                detected_language=result.get("language"),
                processing_time=processing_time,
            )
            return SummaryResult(summary=result["summary"], tags=result["tags"], metadata=metadata)
        return SummaryResult(summary=result["summary"], tags=result["tags"])

    def _summarize_direct(self, text: str) -> dict[str, Any]:
        """Directly summarize text without chunking."""
        prompt = self._build_prompt(text, is_chunk=False)
        response = self.adapter.call(prompt)
        result = self.adapter.parse_response(response)

        # Validate result
        if len(result["tags"]) < 3:
            msg = f"Expected at least 3 tags, got {len(result['tags'])}"
            raise ValidationError(msg)

        return result

    def _summarize_chunked(self, text: str, word_count: int, progress_emitter: Any | None = None) -> dict[str, Any]:
        """Summarize text using chunking and hierarchical summarization."""
        # Split into chunks
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)

        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            prompt = self._build_prompt(chunk.content, is_chunk=True)
            response = self.adapter.call(prompt)
            chunk_result = self.adapter.parse_response(response)
            chunk_summaries.append(chunk_result["summary"])

            if progress_emitter:
                progress_emitter.update(1)

        # Combine chunk summaries
        combined = "\n\n".join(chunk_summaries)

        # If combined summaries are still too large, recursively summarize
        if len(combined.split()) > self.chunk_size:
            return self._summarize_chunked(combined, len(combined.split()), progress_emitter)

        # Final summarization of combined chunks
        final_result = self._summarize_direct(combined)
        if progress_emitter:
            progress_emitter.update(1)
        return final_result


def create_summarizer(
    llm_client: Any | None = None,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    model: str = "llama3.2:latest",
    provider: str = "ollama",
) -> TextSummarizer:
    """
    Create a text summarizer instance.

    Args:
        llm_client: Optional custom LLM client (uses default if None)
        chunk_size: Words per chunk for large texts (auto-detected if None)
        chunk_overlap: Overlap words between chunks (auto-detected if None)
        model: Model name to use (default: "llama3.2:latest")
        provider: Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

    Returns:
        TextSummarizer instance

    Raises:
        ValueError: If chunk_size < chunk_overlap or invalid values
    """
    return TextSummarizer(
        llm_client=llm_client,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        model=model,
        provider=provider,
    )


def summarize_text(
    text: str,
    *,
    include_metadata: bool = True,
    model: str = "llama3.2:latest",
    provider: str = "ollama",
) -> SummaryResult:
    """
    Summarize input text and generate categorization tags.

    Args:
        text: Input text to summarize (UTF-8 encoded)
        include_metadata: Whether to include processing metadata
        model: Model name to use (default: "llama3.2:latest")
        provider: Provider to use - "ollama", "lmstudio", or "mlx" (default: "ollama")

    Returns:
        SummaryResult with summary, tags (≥3), and optional metadata

    Raises:
        InvalidInputError: If text is empty or invalid UTF-8
        LLMError: If LLM client fails
        ValidationError: If output doesn't meet requirements (e.g., <3 tags)
    """
    summarizer = create_summarizer(model=model, provider=provider)
    return summarizer.summarize(text, include_metadata=include_metadata)
