"""Contract tests for LLM Client public API.

These tests define the expected behavior of the public llm_client API.
All tests should FAIL until implementation is complete.
"""

import pytest

from anyfile_to_ai.llm_client.exceptions import GenerationError
from provider_env import (
    check_lmstudio_available,
    check_ollama_available,
    generation_skip_reason,
    resolve_base_url,
    resolve_text_provider,
)


def _require_text_provider():
    provider, base_url, text_model, reason = resolve_text_provider()
    if reason:
        pytest.skip(reason)
    return provider, base_url, text_model


def _require_text_service():
    provider, base_url, text_model = _require_text_provider()
    if provider == "ollama" and not check_ollama_available(base_url):
        pytest.skip(f"Ollama service not available at {base_url}")
    if provider == "lmstudio" and not check_lmstudio_available(base_url):
        pytest.skip(f"LM Studio service not available at {base_url}")
    return provider, base_url, text_model


def _pick_text_model(client, requested_model: str | None) -> str:
    models = client.list_models()
    if not models:
        pytest.skip("No models available in provider runtime")

    if requested_model:
        available = {model.id for model in models}
        if requested_model in available:
            return requested_model
        pytest.skip(f"TEXT_MODEL not available: {requested_model}")

    return models[0].id


def _generate_or_skip(client, request, provider: str):
    try:
        return client.generate(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, provider)
        if skip_reason:
            pytest.skip(skip_reason)
        raise


class TestLLMClientAPI:
    """Contract tests for public LLM client API."""

    def test_create_client_with_config(self):
        """Client can be created with LLMConfig."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig

        provider, base_url, _ = _require_text_provider()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        assert client is not None
        assert client.config == config

    def test_create_client_with_defaults(self):
        """Client can be created with minimal config."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig

        provider, base_url, _ = _require_text_provider()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        # Should have default values from config
        assert client.config.timeout == 30.0
        assert client.config.max_retries == 3

    def test_generate_with_simple_message(self):
        """Client can generate completion from simple message."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url, max_retries=0)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Hello, world!")], model=model)

        response = _generate_or_skip(client, request, provider)

        assert response is not None
        assert response.content
        assert isinstance(response.content, str)
        assert response.provider == provider
        assert response.model

    def test_generate_with_multiple_messages(self):
        """Client can handle conversation with multiple messages."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url, max_retries=0)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(
            messages=[
                Message(role="system", content="You are a helpful assistant."),
                Message(role="user", content="What is 2+2?"),
            ],
            model=model,
        )

        response = _generate_or_skip(client, request, provider)

        assert response is not None
        assert response.content
        assert len(response.content) > 0

    def test_generate_with_model_selection(self):
        """Client can generate with specific model."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url, max_retries=0)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=model)

        response = _generate_or_skip(client, request, provider)

        assert response.model == model

    def test_list_models_returns_list(self):
        """Client can list available models."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, ModelInfo

        provider, base_url, _ = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        models = client.list_models()

        assert isinstance(models, list)
        assert len(models) >= 0  # May be empty if no models installed

        if models:
            assert isinstance(models[0], ModelInfo)
            assert models[0].id
            assert models[0].provider == provider

    def test_list_models_uses_cache(self):
        """Second call to list_models uses cache (faster)."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig
        import time

        provider, base_url, _ = _require_text_service()
        config = LLMConfig(
            provider=provider,
            base_url=base_url,
            cache_ttl=60,  # 1 minute cache
        )
        client = LLMClient(config)

        # First call - goes to API
        start = time.time()
        models1 = client.list_models()
        first_duration = time.time() - start

        # Second call - should use cache
        start = time.time()
        models2 = client.list_models()
        second_duration = time.time() - start

        assert models1 == models2
        assert second_duration < first_duration  # Cache is faster

    def test_invalidate_cache(self):
        """Client can invalidate model list cache."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig

        provider, base_url, _ = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        # Populate cache
        client.list_models()

        # Invalidate
        client.invalidate_cache()

        # Next call should fetch fresh
        models = client.list_models()
        assert isinstance(models, list)

    def test_response_includes_usage_stats(self):
        """Response includes token usage statistics."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Say 'hi'")], model=model)

        response = _generate_or_skip(client, request, provider)

        # Usage may be None for providers that don't support it
        if response.usage:
            assert response.usage.prompt_tokens >= 0
            assert response.usage.completion_tokens >= 0
            assert response.usage.total_tokens >= 0

    def test_response_includes_latency(self):
        """Response includes latency measurement."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=model)

        response = _generate_or_skip(client, request, provider)

        assert response.latency_ms > 0


class TestErrorHandlingContracts:
    """Contract tests for error handling behavior."""

    def test_connection_error_when_service_unreachable(self):
        """Client raises ConnectionError when service is unreachable."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message
        from anyfile_to_ai.llm_client.exceptions import ConnectionError

        provider, _, _ = _require_text_provider()
        config = LLMConfig(
            provider=provider,
            base_url="http://localhost:9999",  # Non-existent port
            max_retries=0,  # No retries for faster test
        )
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        with pytest.raises(ConnectionError):
            client.generate(request)

    def test_validation_error_on_empty_messages(self):
        """Client raises ValidationError for empty message list."""
        from anyfile_to_ai.llm_client import LLMRequest
        from anyfile_to_ai.llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(messages=[])

    def test_validation_error_on_invalid_temperature(self):
        """Client raises ValidationError for invalid temperature."""
        from anyfile_to_ai.llm_client import LLMRequest, Message
        from anyfile_to_ai.llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(
                messages=[Message(role="user", content="Hello")],
                temperature=3.0,  # Out of range
            )

    def test_timeout_error_on_slow_response(self):
        """Client raises TimeoutError when request exceeds timeout."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message
        from anyfile_to_ai.llm_client.exceptions import TimeoutError

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(
            provider=provider,
            base_url=base_url,
            timeout=0.001,  # Very short timeout
        )
        client = LLMClient(config)
        if not text_model:
            pytest.skip("Set TEXT_MODEL to run timeout contract deterministically")
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=text_model)

        with pytest.raises(TimeoutError):
            client.generate(request)


class TestRetryAndFallbackContracts:
    """Contract tests for retry and fallback behavior."""

    def test_retry_on_transient_failure(self):
        """Client retries on transient failures."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        provider, base_url, text_model = _require_text_service()
        config = LLMConfig(provider=provider, base_url=base_url, max_retries=3)
        client = LLMClient(config)

        model = _pick_text_model(client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=model)

        response = _generate_or_skip(client, request, provider)

        # If request succeeded after retries
        assert response.retry_count >= 0

    def test_fallback_to_secondary_provider(self):
        """Client falls back to secondary provider on primary failure."""
        from anyfile_to_ai.llm_client import LLMClient, LLMConfig, LLMRequest, Message

        primary_provider, _, text_model = _require_text_provider()
        fallback_provider = "lmstudio" if primary_provider == "ollama" else "ollama"
        fallback_base_url = resolve_base_url(fallback_provider, "http://localhost:1234" if fallback_provider == "lmstudio" else "http://localhost:11434")

        if fallback_provider == "ollama" and not check_ollama_available(fallback_base_url):
            pytest.skip(f"Ollama service not available at {fallback_base_url}")
        if fallback_provider == "lmstudio" and not check_lmstudio_available(fallback_base_url):
            pytest.skip(f"LM Studio service not available at {fallback_base_url}")

        fallback_config = LLMConfig(provider=fallback_provider, base_url=fallback_base_url)

        config = LLMConfig(
            provider=primary_provider,
            base_url="http://localhost:9999",  # Non-existent
            max_retries=0,
            fallback_configs=[fallback_config],
        )

        client = LLMClient(config)
        fallback_client = LLMClient(fallback_config)

        model = _pick_text_model(fallback_client, text_model)
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=model)

        response = _generate_or_skip(client, request, primary_provider)

        assert response.used_fallback is True
        assert response.fallback_provider == fallback_provider
