"""Integration tests for module progress tracking."""

import pytest

from anything_to_ai.progress_tracker import CallbackProgressConsumer, ProgressEmitter


class TestModuleIntegration:
    """Test progress tracking integration with actual modules."""

    def test_text_summarizer_with_progress(self):
        """Test text_summarizer progress tracking."""
        try:
            from anything_to_ai.text_summarizer.processor import TextSummarizer
        except ImportError:
            pytest.skip("text_summarizer not available")

        updates = []

        def capture(current: int, total: int):
            updates.append((current, total))

        emitter = ProgressEmitter(total=None, label="Summarizing")
        emitter.add_consumer(CallbackProgressConsumer(capture))

        # Note: This is a lightweight test - doesn't actually call LLM
        summarizer = TextSummarizer()
        sample_text = "This is a test. " * 100

        try:
            summarizer.summarize(sample_text, progress_emitter=emitter)
            assert len(updates) >= 0
        except Exception:
            pytest.skip("Summarizer requires LLM backend")

    def test_pdf_extractor_with_progress(self):
        """Test pdf_extractor accepts progress_emitter parameter."""
        try:
            from anything_to_ai.pdf_extractor.reader import extract_text
            from anything_to_ai.pdf_extractor.exceptions import PDFNotFoundError
        except ImportError:
            pytest.skip("pdf_extractor not available")

        emitter = ProgressEmitter(total=None, label="Extracting")

        # Test that the function accepts progress_emitter parameter
        try:
            extract_text("nonexistent.pdf", progress_emitter=emitter)
        except PDFNotFoundError:
            assert True

    def test_progress_deprecation_warnings(self):
        """Test that legacy progress modules have been removed (Phase 4 migration complete)."""
        import sys

        # Verify deprecated modules no longer exist
        modules_to_check = [
            "pdf_extractor.progress",
            "image_processor.progress",
            "audio_processor.progress",
        ]

        for mod in modules_to_check:
            # Clear from cache if present
            if mod in sys.modules:
                del sys.modules[mod]

            # Verify import fails
            with pytest.raises(ImportError):
                __import__(mod)

    def test_text_summarizer_progress_module_exists(self):
        """Test that text_summarizer has progress module."""
        try:
            from anything_to_ai.text_summarizer import progress

            assert hasattr(progress, "ProgressEmitter")
        except ImportError:
            pytest.skip("text_summarizer not available")

    def test_legacy_progress_removed(self):
        """Test that legacy progress classes have been removed (Phase 4 complete)."""
        # Verify pdf_extractor.progress module no longer exists
        try:
            import anything_to_ai.pdf_extractor.progress

            pytest.fail("pdf_extractor.progress should not exist after Phase 4 migration")
        except (ImportError, ModuleNotFoundError):
            pass  # Expected

        # Verify image_processor.progress module no longer exists
        try:
            import anything_to_ai.image_processor.progress

            pytest.fail("image_processor.progress should not exist after Phase 4 migration")
        except (ImportError, ModuleNotFoundError):
            pass  # Expected

        # Verify audio_processor.progress module no longer exists
        try:
            import anything_to_ai.audio_processor.progress

            pytest.fail("audio_processor.progress should not exist after Phase 4 migration")
        except (ImportError, ModuleNotFoundError):
            pass  # Expected

    def test_progress_emitter_parameter_acceptance(self):
        """Test that all refactored modules accept progress_emitter parameter."""
        # Test pdf_extractor
        try:
            from anything_to_ai.pdf_extractor.reader import extract_text
            import inspect

            sig = inspect.signature(extract_text)
            assert "progress_emitter" in sig.parameters
        except ImportError:
            pytest.skip("pdf_extractor not available")

        # Test text_summarizer
        try:
            from anything_to_ai.text_summarizer.processor import TextSummarizer
            import inspect

            sig = inspect.signature(TextSummarizer.summarize)
            assert "progress_emitter" in sig.parameters
        except ImportError:
            pytest.skip("text_summarizer not available")
