"""Integration tests for backward compatibility.

These tests ensure that existing PDF extraction functionality continues to work
unchanged when enhanced features are added.
All tests should FAIL initially until implementation is complete.
"""

import pytest
from unittest.mock import Mock, patch


# Test fixtures
@pytest.fixture
def sample_pdf():
    """Mock PDF file for testing."""
    return "sample-data/pdfs/text-only.pdf"


class TestExistingAPICompatibility:
    """Test that existing API continues to work unchanged."""

    def test_original_extract_text_function(self, sample_pdf):
        """Test that original extract_text function works unchanged."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text

            with patch("os.path.exists", return_value=True):
                # Mock pdfplumber
                with patch("pdfplumber.open") as mock_pdf:
                    mock_page = Mock()
                    mock_page.extract_text.return_value = "Sample text"
                    mock_pdf.return_value.pages = [mock_page]
                    mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                    result = extract_text(sample_pdf)

                    # Should return original ExtractionResult
                    assert hasattr(result, "success")
                    assert hasattr(result, "pages")
                    assert hasattr(result, "total_pages")
                    assert hasattr(result, "processing_time")

                    # Should NOT have enhanced fields
                    assert not hasattr(result, "total_images_found")
                    assert not hasattr(result, "enhanced_pages")

        except ImportError:
            pytest.fail("Original extract_text function not available")

    def test_original_extract_text_streaming(self, sample_pdf):
        """Test that original streaming function works unchanged."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text_streaming
            from anyfile_to_ai.pdf_extractor.models import ExtractionConfig

            config = ExtractionConfig()

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Sample text"
                mock_pdf.return_value.pages = [mock_page]
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                stream = extract_text_streaming(sample_pdf, config)

                pages = list(stream)
                assert len(pages) > 0

                # Should return original PageResult objects
                for page in pages:
                    assert hasattr(page, "page_number")
                    assert hasattr(page, "text")
                    assert hasattr(page, "char_count")
                    assert hasattr(page, "extraction_time")

                    # Should NOT have enhanced fields
                    assert not hasattr(page, "images_found")
                    assert not hasattr(page, "enhanced_text")

        except ImportError:
            pytest.fail("Original extract_text_streaming function not available")

    def test_original_models_unchanged(self):
        """Test that original data models remain unchanged."""
        try:
            from anyfile_to_ai.pdf_extractor.models import (
                PDFDocument,
                PageResult,
                ExtractionResult,
                ExtractionConfig,
            )

            # Test original model structures
            config = ExtractionConfig()
            assert hasattr(config, "streaming_enabled")
            assert hasattr(config, "progress_callback")
            assert hasattr(config, "output_format")

            page = PageResult(page_number=1, text="test", char_count=4, extraction_time=1.0)
            assert hasattr(page, "page_number")
            assert hasattr(page, "text")
            assert hasattr(page, "char_count")
            assert hasattr(page, "extraction_time")

            result = ExtractionResult(
                success=True,
                pages=[page],
                total_pages=1,
                total_chars=4,
                processing_time=1.0,
            )
            assert hasattr(result, "success")
            assert hasattr(result, "pages")
            assert hasattr(result, "total_pages")

        except ImportError:
            pytest.fail("Original models not available")


class TestCLIBackwardCompatibility:
    """Test CLI backward compatibility."""

    def test_original_cli_commands(self, sample_pdf):
        """Test that original CLI commands work unchanged."""
        try:
            from anyfile_to_ai.pdf_extractor.cli import PDFExtractorCLI

            cli = PDFExtractorCLI()

            with patch("os.path.exists", return_value=True):
                # Original argument structure should work
                args = cli.parse_args([sample_pdf])

                assert args.file_path == sample_pdf
                # Should have original arguments
                assert hasattr(args, "stream")
                assert hasattr(args, "output")

                # Should NOT have enhanced arguments by default
                if hasattr(args, "include_images"):
                    assert args.include_images is False

        except (ImportError, AttributeError):
            pytest.fail("Original CLI interface not available or changed")

    def test_cli_output_format_compatibility(self, sample_pdf):
        """Test that CLI output formats remain compatible."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Sample text content"
                mock_pdf.return_value.pages = [mock_page]
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                result = extract_text(sample_pdf)

                # Convert to CLI output format
                from anyfile_to_ai.pdf_extractor.cli import format_output

                # Plain text format should work
                text_output = format_output(result, "plain")
                assert "Sample text content" in text_output

                # JSON format should work
                json_output = format_output(result, "json")
                assert "success" in json_output
                assert "pages" in json_output

        except ImportError:
            pytest.fail("CLI output formatting not available")


class TestExceptionBackwardCompatibility:
    """Test exception backward compatibility."""

    def test_original_exceptions_available(self):
        """Test that original exceptions are still available."""
        try:
            from anyfile_to_ai.pdf_extractor.exceptions import (
                PDFExtractionError,
                PDFNotFoundError,
                PDFCorruptedError,
                PDFPasswordProtectedError,
                PDFNoTextError,
            )

            # Should be able to create instances
            base_error = PDFExtractionError("test error")
            not_found_error = PDFNotFoundError("test.pdf")
            corrupted_error = PDFCorruptedError("test.pdf", "corruption details")

            assert isinstance(base_error, Exception)
            assert isinstance(not_found_error, PDFExtractionError)
            assert isinstance(corrupted_error, PDFExtractionError)

        except ImportError:
            pytest.fail("Original exceptions not available")

    def test_exception_hierarchy_preserved(self):
        """Test that original exception hierarchy is preserved."""
        try:
            from anyfile_to_ai.pdf_extractor.exceptions import (
                PDFExtractionError,
                PDFNotFoundError,
                PDFCorruptedError,
            )

            # Original hierarchy should be maintained
            assert issubclass(PDFNotFoundError, PDFExtractionError)
            assert issubclass(PDFCorruptedError, PDFExtractionError)
            assert issubclass(PDFExtractionError, Exception)

        except ImportError:
            pytest.fail("Original exception hierarchy not preserved")


class TestModuleImportCompatibility:
    """Test module import backward compatibility."""

    def test_original_imports_work(self):
        """Test that original import statements continue to work."""
        try:
            # All original imports should work (except deprecated progress.py)
            from anyfile_to_ai.pdf_extractor import (
                extract_text,
                extract_text_streaming,
            )
            from anyfile_to_ai.pdf_extractor.models import (
                PDFDocument,
                PageResult,
                ExtractionResult,
            )
            from anyfile_to_ai.pdf_extractor.exceptions import PDFExtractionError

            # Note: pdf_extractor.progress was deprecated and removed in Phase 4
            # Use progress_tracker.ProgressEmitter instead

            # Should be importable
            assert callable(extract_text)
            assert callable(extract_text_streaming)

        except ImportError as e:
            pytest.fail(f"Original imports broken: {e}")

    def test_module_structure_preserved(self):
        """Test that original module structure is preserved."""
        try:
            import anyfile_to_ai.pdf_extractor

            # Check __all__ includes original exports
            expected_exports = {
                "extract_text",
                "extract_text_streaming",
                "get_pdf_info",
                "PDFDocument",
                "PageResult",
                "ExtractionResult",
                "ExtractionConfig",
                "PDFExtractionError",
                "PDFNotFoundError",
                "PDFCorruptedError",
            }

            actual_exports = set(pdf_extractor.__all__)
            assert expected_exports.issubset(actual_exports)

        except ImportError:
            pytest.fail("Module structure changed")


class TestBehavioralCompatibility:
    """Test behavioral backward compatibility."""

    def test_same_output_for_same_input(self, sample_pdf):
        """Test that same input produces same output as before enhancement."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text
            from anyfile_to_ai.pdf_extractor.models import ExtractionConfig

            # Standard configuration without enhancements
            config = ExtractionConfig(output_format="plain")

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Expected text content"
                mock_pdf.return_value.pages = [mock_page]
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                result = extract_text(sample_pdf, config)

                # Result structure should be identical to pre-enhancement
                assert result.success is True
                assert len(result.pages) == 1
                assert result.pages[0].text == "Expected text content"
                assert result.total_pages == 1
                assert result.processing_time > 0

        except ImportError:
            pytest.fail("Behavioral compatibility broken")

    def test_error_handling_unchanged(self):
        """Test that error handling behavior is unchanged."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text
            from anyfile_to_ai.pdf_extractor.exceptions import PDFNotFoundError

            # Should still raise PDFNotFoundError for missing files
            with pytest.raises(PDFNotFoundError):
                extract_text("nonexistent.pdf")

        except ImportError:
            pytest.fail("Error handling compatibility broken")

    def test_performance_not_degraded(self, sample_pdf):
        """Test that performance is not degraded for original functionality."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text
            import time

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Test content"
                mock_pdf.return_value.pages = [mock_page] * 10  # 10 pages
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                start_time = time.time()
                result = extract_text(sample_pdf)
                end_time = time.time()

                # Should complete quickly without image processing overhead
                processing_time = end_time - start_time
                assert processing_time < 5.0  # Should be fast

                # Should process all pages
                assert result.total_pages == 10

        except ImportError:
            pytest.fail("Performance compatibility issue")


class TestConfigurationCompatibility:
    """Test configuration backward compatibility."""

    def test_original_config_parameters_work(self, sample_pdf):
        """Test that original configuration parameters continue to work."""
        try:
            from anyfile_to_ai.pdf_extractor import extract_text_streaming
            from anyfile_to_ai.pdf_extractor.models import ExtractionConfig

            # Original config should work
            config = ExtractionConfig(streaming_enabled=True, output_format="json")

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Content"
                mock_pdf.return_value.pages = [mock_page]
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                stream = extract_text_streaming(sample_pdf, config)
                pages = list(stream)

                assert len(pages) > 0
                assert pages[0].text == "Content"

        except ImportError:
            pytest.fail("Configuration compatibility broken")

    def test_config_validation_preserved(self):
        """Test that original configuration validation is preserved."""
        try:
            from anyfile_to_ai.pdf_extractor.models import ExtractionConfig

            # Invalid output format should still raise ValueError
            with pytest.raises(ValueError):
                ExtractionConfig(output_format="invalid_format")

        except ImportError:
            pytest.fail("Configuration validation compatibility broken")


class TestDeprecationWarnings:
    """Test for proper deprecation warnings if any changes are made."""

    def test_no_unexpected_deprecation_warnings(self, sample_pdf):
        """Test that no unexpected deprecation warnings are introduced."""
        import warnings

        try:
            from anyfile_to_ai.pdf_extractor import extract_text

            with patch("os.path.exists", return_value=True), patch("pdfplumber.open") as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Content"
                mock_pdf.return_value.pages = [mock_page]
                mock_pdf.return_value.__enter__.return_value = mock_pdf.return_value

                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")

                    extract_text(sample_pdf)

                    # Should not generate deprecation warnings for normal usage
                    deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
                    assert len(deprecation_warnings) == 0, f"Unexpected deprecation warnings: {deprecation_warnings}"

        except ImportError:
            pytest.fail("Cannot test deprecation warnings - imports broken")
