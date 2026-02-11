"""Contract tests for LLM provider adapter interface.

These tests define the expected behavior of provider adapters.
All tests should FAIL until implementation is complete.
"""

import os
import pytest

from provider_env import (
    check_lmstudio_available,
    check_ollama_available,
    generation_skip_reason,
    mlx_available,
    provider_mismatch_reason,
    resolve_base_url,
    resolve_text_model,
    resolve_vision_model,
)
from anyfile_to_ai.llm_client.exceptions import GenerationError

OLLAMA_BASE_URL = resolve_base_url("ollama", "http://localhost:11434")
LMSTUDIO_BASE_URL = resolve_base_url("lmstudio", "http://localhost:1234")
REQUESTED_TEXT_MODEL = resolve_text_model(os.environ.get("LMSTUDIO_MODEL"))
VISION_MODEL = resolve_vision_model(ignore_defaulted=True)

_OLLAMA_SKIP_REASON = provider_mismatch_reason("ollama")
if not _OLLAMA_SKIP_REASON and not check_ollama_available(OLLAMA_BASE_URL):
    _OLLAMA_SKIP_REASON = f"Ollama service not available at {OLLAMA_BASE_URL}"

_LMSTUDIO_SKIP_REASON = provider_mismatch_reason("lmstudio")
if not _LMSTUDIO_SKIP_REASON and not check_lmstudio_available(LMSTUDIO_BASE_URL):
    _LMSTUDIO_SKIP_REASON = f"LM Studio service not available at {LMSTUDIO_BASE_URL}"

_MLX_SKIP_REASON = provider_mismatch_reason("mlx")
if not _MLX_SKIP_REASON and not VISION_MODEL:
    _MLX_SKIP_REASON = "VISION_MODEL not set"
if not _MLX_SKIP_REASON and not mlx_available():
    _MLX_SKIP_REASON = "mlx-vlm dependency not available"


def _generate_or_skip(adapter, request, provider: str):
    try:
        return adapter.generate(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, provider)
        if skip_reason:
            pytest.skip(skip_reason)
        raise


class TestAdapterInterface:
    """Contract tests for base adapter interface."""

    def test_adapter_has_required_methods(self):
        """Base adapter defines required interface methods."""
        from anyfile_to_ai.llm_client.adapters.base import BaseAdapter

        # Check required methods exist
        assert hasattr(BaseAdapter, "generate")
        assert hasattr(BaseAdapter, "generate_vision")
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

        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)

        adapter = OllamaAdapter(config)

        assert adapter.config == config


@pytest.mark.skipif(
    _OLLAMA_SKIP_REASON is not None,
    reason=_OLLAMA_SKIP_REASON or "",
)
class TestOllamaAdapter:
    """Contract tests for Ollama provider adapter."""

    def test_ollama_adapter_can_generate(self):
        """Ollama adapter can generate completions."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        adapter = OllamaAdapter(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model="deepseek-r1:1.5b")

        response = _generate_or_skip(adapter, request, "ollama")

        assert response is not None
        assert response.content
        assert response.provider == "ollama"

    def test_ollama_adapter_can_list_models(self):
        """Ollama adapter can list available models."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig, ModelInfo

        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        adapter = OllamaAdapter(config)

        models = adapter.list_models()

        assert isinstance(models, list)
        if models:
            assert isinstance(models[0], ModelInfo)

    def test_ollama_adapter_health_check(self):
        """Ollama adapter can check service health."""
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        adapter = OllamaAdapter(config)

        is_healthy = adapter.health_check()

        assert isinstance(is_healthy, bool)


@pytest.mark.skipif(
    _LMSTUDIO_SKIP_REASON is not None,
    reason=_LMSTUDIO_SKIP_REASON or "",
)
class TestLMStudioAdapter:
    """Contract tests for LM Studio provider adapter."""

    def test_lmstudio_adapter_can_generate(self):
        """LM Studio adapter can generate completions."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL)
        adapter = LMStudioAdapter(config)

        models = adapter.list_models()
        if not models:
            pytest.skip("No models available in LM Studio")

        target_model = REQUESTED_TEXT_MODEL or models[0].id
        if REQUESTED_TEXT_MODEL and target_model not in {m.id for m in models}:
            pytest.skip(f"TEXT_MODEL not available: {target_model}")

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=target_model)

        response = _generate_or_skip(adapter, request, "lmstudio")

        assert response is not None
        assert response.content
        assert response.provider == "lmstudio"

    def test_lmstudio_adapter_can_list_models(self):
        """LM Studio adapter can list available models."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig, ModelInfo

        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL)
        adapter = LMStudioAdapter(config)

        models = adapter.list_models()

        assert isinstance(models, list)
        if models:
            assert isinstance(models[0], ModelInfo)

    def test_lmstudio_supports_authentication(self):
        """LM Studio adapter supports API key authentication."""
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client import LLMConfig

        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, api_key="test-key")
        adapter = LMStudioAdapter(config)

        assert adapter.config.api_key == "test-key"


@pytest.mark.skipif(_MLX_SKIP_REASON is not None, reason=_MLX_SKIP_REASON or "")
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

        request = LLMRequest(messages=[Message(role="user", content="Describe sample-data/images/ui-screenshot.png")])

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

        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
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
