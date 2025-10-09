"""Data models for text summarizer module."""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class SummaryRequest(BaseModel):
    """Request to summarize text."""

    text: str = Field(..., min_length=1, description="Text to summarize")
    format: Literal["json", "plain"] = Field(default="json", description="Output format")
    include_metadata: bool = Field(default=True, description="Include processing metadata")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that text is not empty or whitespace-only."""
        if not v or not v.strip():
            msg = "Text must not be empty or whitespace-only"
            raise ValueError(msg)
        return v


class SummaryMetadata(BaseModel):
    """Processing metadata for a summarization operation."""

    input_length: int = Field(..., gt=0, description="Word count of input")
    chunked: bool = Field(..., description="Whether text was chunked")
    chunk_count: int | None = Field(default=None, ge=1, description="Number of chunks")
    detected_language: str | None = Field(default=None, description="ISO 639-1 language code")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")

    @field_validator("chunk_count")
    @classmethod
    def validate_chunk_count(cls, v: int | None, info) -> int | None:
        """Validate chunk_count is provided when chunked=True."""
        values = info.data
        if values.get("chunked") and v is None:
            msg = "chunk_count required when chunked=True"
            raise ValueError(msg)
        return v


class SummaryResult(BaseModel):
    """Result of text summarization."""

    summary: str = Field(..., min_length=1, description="Generated summary")
    tags: list[str] = Field(..., min_length=3, description="Content tags (minimum 3)")
    metadata: SummaryMetadata | None = Field(default=None, description="Processing metadata")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that there are at least 3 non-empty tags."""
        if len(v) < 3:
            msg = "Must have at least 3 tags"
            raise ValueError(msg)
        if any(not tag.strip() for tag in v):
            msg = "Tags must be non-empty strings"
            raise ValueError(msg)
        return v


class TextChunk(BaseModel):
    """A chunk of text for processing large documents."""

    index: int = Field(..., ge=0, description="Chunk index")
    content: str = Field(..., min_length=1, description="Chunk text content")
    start_word: int = Field(..., ge=0, description="Start word index")
    end_word: int = Field(..., gt=0, description="End word index")

    @field_validator("end_word")
    @classmethod
    def validate_word_range(cls, v: int, info) -> int:
        """Validate that end_word is greater than start_word."""
        values = info.data
        start = values.get("start_word", 0)
        if v <= start:
            msg = "end_word must be greater than start_word"
            raise ValueError(msg)
        return v
