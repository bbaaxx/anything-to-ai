"""Contract tests for text_summarizer API.

These tests define the expected behavior of the public API.
They should fail initially and pass after implementation.
"""

import pytest
from anyfile_to_ai.text_summarizer import (
    summarize_text,
    create_summarizer,
    chunk_text,
    SummaryResult,
    TextSummarizer,
    TextChunk,
    InvalidInputError,
)


class TestSummarizeText:
    """Contract tests for summarize_text function."""

    def test_valid_input_returns_summary_result(self):
        """Test that valid input returns a SummaryResult object."""
        text = "Machine learning is transforming industries. AI applications are growing."
        result = summarize_text(text)
        assert isinstance(result, SummaryResult)

    def test_result_has_non_empty_summary(self):
        """Test that result contains a non-empty summary."""
        text = "Cloud computing enables scalability. Distributed systems are essential."
        result = summarize_text(text)
        assert result.summary
        assert len(result.summary.strip()) > 0

    def test_result_has_minimum_three_tags(self):
        """Test that result contains at least 3 tags."""
        text = "Natural language processing helps computers understand text. NLP is evolving."
        result = summarize_text(text)
        assert len(result.tags) >= 3

    def test_metadata_included_by_default(self):
        """Test that metadata is included when include_metadata=True (default)."""
        text = "Quantum computing promises exponential speedups for certain problems."
        result = summarize_text(text, include_metadata=True)
        assert result.metadata is not None
        assert result.metadata.input_length > 0

    def test_metadata_excluded_when_flag_false(self):
        """Test that metadata is excluded when include_metadata=False."""
        text = "Blockchain technology provides decentralized consensus mechanisms."
        result = summarize_text(text, include_metadata=False)
        assert result.metadata is None

    def test_raises_invalid_input_error_for_empty_text(self):
        """Test that empty text raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            summarize_text("")

    def test_raises_invalid_input_error_for_whitespace_only(self):
        """Test that whitespace-only text raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            summarize_text("   \n\t  ")

    def test_handles_small_text_under_1k_words(self):
        """Test handling of small text (<1000 words)."""
        text = "Short text. " * 50  # ~100 words
        result = summarize_text(text)
        assert isinstance(result, SummaryResult)
        if result.metadata:
            assert result.metadata.input_length < 1000
            assert not result.metadata.chunked

    def test_handles_medium_text_1k_to_10k_words(self):
        """Test handling of medium text (1000-10000 words)."""
        text = "Medium length sentence with multiple words. " * 200  # ~1400 words
        result = summarize_text(text)
        assert isinstance(result, SummaryResult)
        if result.metadata:
            assert 1000 <= result.metadata.input_length <= 10000

    def test_handles_large_text_over_10k_words_with_chunking(self):
        """Test handling of large text (>10000 words) with chunking."""
        text = "This is a longer sentence with several words in it. " * 1200  # ~12000 words
        result = summarize_text(text)
        assert isinstance(result, SummaryResult)
        if result.metadata:
            assert result.metadata.input_length > 10000
            assert result.metadata.chunked is True
            assert result.metadata.chunk_count is not None
            assert result.metadata.chunk_count > 1

    def test_handles_non_english_text(self):
        """Test handling of non-English text (multilingual support)."""
        # Spanish text
        text = "La inteligencia artificial está transformando el mundo. Los algoritmos de aprendizaje automático procesan datos. Esta tecnología se aplica en medicina y finanzas."
        result = summarize_text(text)
        assert isinstance(result, SummaryResult)
        # Summary and tags should be in English
        assert result.summary
        assert len(result.tags) >= 3


class TestCreateSummarizer:
    """Contract tests for create_summarizer factory function."""

    def test_creates_with_default_client(self):
        """Test that create_summarizer works with default LLM client."""
        summarizer = create_summarizer()
        assert isinstance(summarizer, TextSummarizer)

    def test_creates_with_custom_client(self):
        """Test that create_summarizer accepts custom LLM client."""

        # Mock client - in real impl, this would be from anyfile_to_ai.llm_client module
        class MockClient:
            pass

        custom_client = MockClient()
        summarizer = create_summarizer(llm_client=custom_client)
        assert isinstance(summarizer, TextSummarizer)

    def test_sets_custom_chunk_size(self):
        """Test that custom chunk_size is accepted."""
        summarizer = create_summarizer(chunk_size=5000)
        assert isinstance(summarizer, TextSummarizer)

    def test_sets_custom_chunk_overlap(self):
        """Test that custom chunk_overlap is accepted."""
        summarizer = create_summarizer(chunk_overlap=200)
        assert isinstance(summarizer, TextSummarizer)

    def test_raises_value_error_if_chunk_size_less_than_overlap(self):
        """Test that ValueError is raised if chunk_size < chunk_overlap."""
        with pytest.raises(ValueError, match="chunk_size.*chunk_overlap"):
            create_summarizer(chunk_size=100, chunk_overlap=200)

    def test_raises_value_error_for_invalid_chunk_size(self):
        """Test that ValueError is raised for invalid chunk_size."""
        with pytest.raises(ValueError):
            create_summarizer(chunk_size=0)
        with pytest.raises(ValueError):
            create_summarizer(chunk_size=-100)

    def test_raises_value_error_for_negative_overlap(self):
        """Test that ValueError is raised for negative chunk_overlap."""
        with pytest.raises(ValueError):
            create_summarizer(chunk_overlap=-50)


class TestChunkText:
    """Contract tests for chunk_text utility function."""

    def test_returns_single_chunk_for_small_text(self):
        """Test that text smaller than chunk_size returns single chunk."""
        text = "Short text with few words."
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert isinstance(chunks[0], TextChunk)

    def test_returns_multiple_chunks_for_large_text(self):
        """Test that large text returns multiple chunks."""
        text = "Word. " * 15000  # ~15000 words
        chunks = chunk_text(text, chunk_size=10000, overlap=500)
        assert len(chunks) > 1

    def test_chunks_have_sequential_indices(self):
        """Test that chunks have correct sequential indices."""
        text = "Word. " * 15000
        chunks = chunk_text(text, chunk_size=10000, overlap=500)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_chunks_have_correct_word_ranges(self):
        """Test that chunks have correct start_word and end_word."""
        text = "Word. " * 15000
        chunks = chunk_text(text, chunk_size=10000, overlap=500)
        for chunk in chunks:
            assert chunk.start_word >= 0
            assert chunk.end_word > chunk.start_word

    def test_chunks_overlap_by_specified_amount(self):
        """Test that consecutive chunks overlap correctly."""
        text = "Word. " * 15000
        overlap = 500
        chunks = chunk_text(text, chunk_size=10000, overlap=overlap)
        if len(chunks) > 1:
            # Second chunk should start before first chunk ends
            assert chunks[1].start_word < chunks[0].end_word

    def test_raises_value_error_for_empty_text(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError):
            chunk_text("")
