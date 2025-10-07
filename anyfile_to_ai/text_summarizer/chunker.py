"""Text chunking for large documents."""

from .models import TextChunk


def chunk_text(
    text: str,
    chunk_size: int = 10000,
    overlap: int = 500,
) -> list[TextChunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target words per chunk (default: 10000)
        overlap: Overlap words between chunks (default: 500)

    Returns:
        List of TextChunk objects with sequential indices

    Raises:
        ValueError: If text is empty or invalid parameters
    """
    if not text or not text.strip():
        raise ValueError("Text must not be empty")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0:
        raise ValueError("overlap must be non-negative")

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    # Split text into words
    words = text.split()

    # If text is smaller than chunk_size, return single chunk
    if len(words) <= chunk_size:
        return [
            TextChunk(
                index=0,
                content=text,
                start_word=0,
                end_word=len(words),
            ),
        ]

    # Create chunks with overlap
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunks.append(
            TextChunk(
                index=chunk_index,
                content=chunk_content,
                start_word=start,
                end_word=end,
            ),
        )

        chunk_index += 1

        # Move start forward, accounting for overlap
        if end >= len(words):
            break  # Last chunk
        start = end - overlap

    return chunks
