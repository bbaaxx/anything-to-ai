"""Unit tests for provider-aware vision dispatch."""

import pytest


class TestVisionProviderDispatch:
    """Validate provider routing and configuration errors."""

    def test_remote_provider_requires_base_url(self, monkeypatch):
        """Remote providers must include BASE_URL for vision."""
        from anyfile_to_ai.image_processor import create_config, process_image
        from anyfile_to_ai.image_processor.exceptions import ProcessingError

        image_path = "sample-data/images/ui-screenshot.png"

        monkeypatch.setenv("PROVIDER", "lmstudio")
        monkeypatch.setenv("VISION_MODEL", "qwen/qwen3-vl-8b")
        monkeypatch.delenv("BASE_URL", raising=False)

        config = create_config(description_style="brief", max_length=200, batch_size=1)

        with pytest.raises(ProcessingError) as exc_info:
            process_image(image_path, config)

        assert "BASE_URL" in str(exc_info.value)

    def test_remote_provider_dispatches_to_llm_client(self, monkeypatch):
        """Provider dispatch uses LLM client for remote vision calls."""
        from anyfile_to_ai.image_processor import create_config, process_image
        from anyfile_to_ai.llm_client.models import VisionResponse

        image_path = "sample-data/images/ui-screenshot.png"

        monkeypatch.setenv("PROVIDER", "ollama")
        monkeypatch.setenv("BASE_URL", "http://localhost:11434")
        monkeypatch.setenv("VISION_MODEL", "qwen/qwen3-vl-8b")

        def fake_generate_vision(self, request):
            return VisionResponse(
                content="Synthetic description",
                model=request.model or "vision-model",
                finish_reason="stop",
                response_id="resp-1",
                provider="ollama",
                latency_ms=12.0,
            )

        monkeypatch.setattr(
            "anyfile_to_ai.llm_client.client.LLMClient.generate_vision",
            fake_generate_vision,
        )

        config = create_config(description_style="detailed", max_length=120, batch_size=1)
        result = process_image(image_path, config)

        assert result.description == "Synthetic description"
        assert result.model_used == "qwen/qwen3-vl-8b"

    def test_unsupported_provider_raises_error(self, monkeypatch):
        """Unsupported providers should raise a configuration error."""
        from anyfile_to_ai.image_processor import create_config, process_image
        from anyfile_to_ai.image_processor.exceptions import ProcessingError

        image_path = "sample-data/images/ui-screenshot.png"

        monkeypatch.setenv("PROVIDER", "unknown")
        monkeypatch.setenv("VISION_MODEL", "qwen/qwen3-vl-8b")
        monkeypatch.delenv("BASE_URL", raising=False)

        config = create_config(description_style="brief", max_length=120, batch_size=1)

        with pytest.raises(ProcessingError) as exc_info:
            process_image(image_path, config)

        assert "PROVIDER" in str(exc_info.value)

    def test_pdf_mlx_provider_does_not_require_base_url(self, monkeypatch):
        """PDF image processing should not require BASE_URL for mlx provider."""
        from anyfile_to_ai.pdf_extractor.enhanced_models import EnhancedExtractionConfig
        from anyfile_to_ai.pdf_extractor.image_integration import PDFImageProcessor

        monkeypatch.setenv("PROVIDER", "mlx")
        monkeypatch.setenv("VISION_MODEL", "mlx-community/Qwen2-VL-2B-Instruct-4bit")
        monkeypatch.delenv("BASE_URL", raising=False)

        processor = PDFImageProcessor(image_processor=None)
        config = EnhancedExtractionConfig(include_images=True)

        processor.validate_config(config)
