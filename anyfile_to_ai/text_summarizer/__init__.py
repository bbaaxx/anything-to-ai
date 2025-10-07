"""Text Summarizer Module.

A module for summarizing text using LLMs and generating categorization tags.
"""

from .models import (
    SummaryRequest,
    SummaryResult,
    SummaryMetadata,
    TextChunk,
)
from .processor import summarize_text, create_summarizer, TextSummarizer
from .chunker import chunk_text
from .exceptions import (
    SummarizerError,
    InvalidInputError,
    LLMError,
    ValidationError,
)

__all__ = [
    "InvalidInputError",
    "LLMError",
    "SummarizerError",
    "SummaryMetadata",
    "SummaryRequest",
    "SummaryResult",
    "TextChunk",
    "TextSummarizer",
    "ValidationError",
    "chunk_text",
    "create_summarizer",
    "summarize_text",
]

__version__ = "1.0.0"
