"""Contract tests for LLM provider adapter interface.

These tests define the expected behavior of provider adapters.
All tests should FAIL until implementation is complete.
"""

import pytest


def check_ollama_available() -> bool:
    """Check if Ollama service is available."""
    try:
        import httpx

        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def check_lmstudio_available() -> bool:
    """Check if LMStudio service is available and has a model loaded."""
    try:
        import httpx

        # Check if service is running
        response = httpx.get("http://localhost:1234/v1/models", timeout=5.0)
        if response.status_code != 200:
            return False

        # Check if any models are loaded
        models = response.json()
        return len(models.get("data", [])) > 0
    except Exception:
        return False


def check_vision_model_set() -> bool:
    """Check if VISION_MODEL environment variable is set."""
    import os

    return bool(os.environ.get("VISION_MODEL"))


class TestAdapterInterface:
    """Contract tests for base adapter interface."""

    def test_adapter_has_required_methods(self):
        """Base adapter defines required interface methods."""
        from anyfile_to_ai.llm_client.adapters.base import BaseAdapter

        # Check required methods exist
        assert hasattr(BaseAdapter, "generate")
        assert hasattr(BaseAdapter, "list_models")
        assert hasattr(BaseAdapter, "health_check")

    def test_adapter_generate_is_abstract(self):
        """Base adapter generate method is abstract."""
        from anyfile_to_ai.llm_client.adapters.base import BaseAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost")

        # Should not be able to instantiate abstract base
        with pytest.raises(TypeError):
            BaseAdapter(config)

    def test_adapter_receives_config(self):
        """Adapter is initialized with LLMConfig."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")

        adapter = OllamaAdapter(config)

        assert adapter.config == config


@pytest.mark.skipif(
    not check_ollama_available(),
    reason="Ollama service not available at localhost:11434",
)
class TestOllamaAdapter:
    """Contract tests for Ollama provider adapter."""

    def test_ollama_adapter_can_generate(self):
        """Ollama adapter can generate completions."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        adapter = OllamaAdapter(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model="deepseek-r1:1.5b")

        response = adapter.generate(request)

        assert response is not None
        assert response.content
        assert response.provider == "ollama"

    def test_ollama_adapter_can_list_models(self):
        """Ollama adapter can list available models."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig, ModelInfo

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        adapter = OllamaAdapter(config)

        models = adapter.list_models()

        assert isinstance(models, list)
        if models:
            assert isinstance(models[0], ModelInfo)

    def test_ollama_adapter_health_check(self):
        """Ollama adapter can check service health."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        adapter = OllamaAdapter(config)

        is_healthy = adapter.health_check()

        assert isinstance(is_healthy, bool)


@pytest.mark.skipif(
    not check_lmstudio_available(),
    reason="LMStudio service not available at localhost:1234",
)
class TestLMStudioAdapter:
    """Contract tests for LM Studio provider adapter."""

    def test_lmstudio_adapter_can_generate(self):
        """LM Studio adapter can generate completions."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="lmstudio", base_url="http://localhost:1234")
        adapter = LMStudioAdapter(config)

        request = LLMRequest(
            messages=[Message(role="user", content="Hello")],
            model="mistralai/magistral-small-2509",
        )

        response = adapter.generate(request)

        assert response is not None
        assert response.content
        assert response.provider == "lmstudio"

    def test_lmstudio_adapter_can_list_models(self):
        """LM Studio adapter can list available models."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig, ModelInfo

        config = LLMConfig(provider="lmstudio", base_url="http://localhost:1234")
        adapter = LMStudioAdapter(config)

        models = adapter.list_models()

        assert isinstance(models, list)
        if models:
            assert isinstance(models[0], ModelInfo)

    def test_lmstudio_supports_authentication(self):
        """LM Studio adapter supports API key authentication."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="lmstudio", base_url="http://localhost:1234", api_key="test-key")
        adapter = LMStudioAdapter(config)

        assert adapter.config.api_key == "test-key"


@pytest.mark.skipif(not check_vision_model_set(), reason="VISION_MODEL environment variable not set")
class TestMLXAdapter:
    """Contract tests for MLX provider adapter."""

    def test_mlx_adapter_can_generate(self):
        """MLX adapter can generate completions."""
        from anyfile_to_ai.llm_client.adapters.mlx_adapter import MLXAdapter
        from anyfile_to_ai.llm_client import LLMConfig, LLMRequest, Message

        config = LLMConfig(
            provider="mlx",
            base_url="local",  # MLX is local
        )
        adapter = MLXAdapter(config)

        request = LLMRequest(messages=[Message(role="user", content="Describe this image")])

        response = adapter.generate(request)

        assert response is not None
        assert response.content
        assert response.provider == "mlx"

    def test_mlx_adapter_wraps_existing_vlm(self):
        """MLX adapter wraps existing mlx-vlm functionality."""
        from anyfile_to_ai.llm_client.adapters.mlx_adapter import MLXAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="mlx", base_url="local")
        adapter = MLXAdapter(config)

        # Should have access to underlying VLM processor
        assert hasattr(adapter, "_vlm_processor") or hasattr(adapter, "vlm_processor")

    def test_mlx_adapter_maintains_compatibility(self):
        """MLX adapter maintains compatibility with image_processor."""
        from anyfile_to_ai.llm_client.adapters.mlx_adapter import MLXAdapter
        from anyfile_to_ai.llm_client import LLMConfig
        import os

        # Should respect VISION_MODEL environment variable
        os.environ["VISION_MODEL"] = "google/gemma-3-4b"

        config = LLMConfig(provider="mlx", base_url="local")
        adapter = MLXAdapter(config)

        # Should initialize without error
        assert adapter is not None


class TestAdapterFactory:
    """Contract tests for adapter factory/registry."""

    def test_get_adapter_for_provider(self):
        """Factory can create adapter for provider."""
        from anyfile_to_ai.llm_client.adapters import get_adapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        adapter = get_adapter(config)

        assert adapter is not None
        assert adapter.config.provider == "ollama"

    def test_get_adapter_raises_for_unknown_provider(self):
        """Factory raises error for unknown provider."""
        from anyfile_to_ai.llm_client.exceptions import ValidationError
        from anyfile_to_ai.llm_client import LLMConfig

        # ValidationError will be raised during config creation for invalid provider
        with pytest.raises(ValidationError):
            LLMConfig(provider="unknown", base_url="http://localhost")

    def test_adapter_registry_has_all_providers(self):
        """Adapter registry includes all supported providers."""
        from anyfile_to_ai.llm_client.adapters import ADAPTER_REGISTRY

        assert "ollama" in ADAPTER_REGISTRY
        assert "lmstudio" in ADAPTER_REGISTRY
        assert "mlx" in ADAPTER_REGISTRY
