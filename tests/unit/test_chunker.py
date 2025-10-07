"""Unit tests for text chunker."""

import pytest
from anything_to_ai.text_summarizer.chunker import chunk_text


class TestChunkText:
    """Unit tests for chunk_text function."""

    def test_empty_text_raises_value_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text must not be empty"):
            chunk_text("")

    def test_whitespace_only_text_raises_value_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="Text must not be empty"):
            chunk_text("   \n\t  ")

    def test_single_word_returns_single_chunk(self):
        """Test that single word returns single chunk."""
        chunks = chunk_text("word")
        assert len(chunks) == 1
        assert chunks[0].content == "word"
        assert chunks[0].index == 0
        assert chunks[0].start_word == 0
        assert chunks[0].end_word == 1

    def test_exact_boundary_at_chunk_size(self):
        """Test text exactly at chunk_size boundary."""
        words = ["word"] * 100
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0].end_word == 100

    def test_one_word_over_boundary(self):
        """Test text with one word over chunk_size."""
        words = ["word"] * 101
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 2

    def test_overlap_calculation(self):
        """Test that overlap is calculated correctly."""
        words = ["w"] * 150
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        # Second chunk should start 80 words after first (100 - 20 overlap)
        if len(chunks) > 1:
            assert chunks[1].start_word == 80

    def test_word_range_accuracy(self):
        """Test that word ranges are accurate."""
        text = " ".join([f"word{i}" for i in range(200)])
        chunks = chunk_text(text, chunk_size=100, overlap=10)

        for chunk in chunks:
            words_in_chunk = chunk.content.split()
            expected_count = chunk.end_word - chunk.start_word
            assert len(words_in_chunk) == expected_count

    def test_invalid_chunk_size_zero(self):
        """Test that chunk_size=0 raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("some text", chunk_size=0)

    def test_invalid_chunk_size_negative(self):
        """Test that negative chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("some text", chunk_size=-10)

    def test_invalid_overlap_negative(self):
        """Test that negative overlap raises ValueError."""
        with pytest.raises(ValueError, match="overlap must be non-negative"):
            chunk_text("some text", chunk_size=100, overlap=-5)

    def test_chunk_size_less_than_equal_overlap(self):
        """Test that chunk_size <= overlap raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be greater than overlap"):
            chunk_text("some text", chunk_size=50, overlap=50)

        with pytest.raises(ValueError, match="chunk_size must be greater than overlap"):
            chunk_text("some text", chunk_size=50, overlap=60)

    def test_all_chunks_have_content(self):
        """Test that all chunks have non-empty content."""
        text = " ".join(["word"] * 500)
        chunks = chunk_text(text, chunk_size=100, overlap=10)

        for chunk in chunks:
            assert len(chunk.content) > 0
            assert len(chunk.content.strip()) > 0

    def test_last_chunk_may_be_smaller(self):
        """Test that the last chunk can be smaller than chunk_size."""
        text = " ".join(["word"] * 150)
        chunks = chunk_text(text, chunk_size=100, overlap=10)

        if len(chunks) > 1:
            last_chunk = chunks[-1]
            word_count = len(last_chunk.content.split())
            # Last chunk should have remaining words
            assert word_count <= 100
