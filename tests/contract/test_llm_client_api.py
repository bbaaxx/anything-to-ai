"""Contract tests for LLM Client public API.

These tests define the expected behavior of the public llm_client API.
All tests should FAIL until implementation is complete.
"""

import pytest


class TestLLMClientAPI:
    """Contract tests for public LLM client API."""

    def test_create_client_with_config(self):
        """Client can be created with LLMConfig."""
        from llm_client import LLMClient, LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        assert client is not None
        assert client.config == config

    def test_create_client_with_defaults(self):
        """Client can be created with minimal config."""
        from llm_client import LLMClient, LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        # Should have default values from config
        assert client.config.timeout == 30.0
        assert client.config.max_retries == 3

    def test_generate_with_simple_message(self):
        """Client can generate completion from simple message."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello, world!")])

        response = client.generate(request)

        assert response is not None
        assert response.content
        assert isinstance(response.content, str)
        assert response.provider == "ollama"
        assert response.model

    def test_generate_with_multiple_messages(self):
        """Client can handle conversation with multiple messages."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        request = LLMRequest(
            messages=[
                Message(role="system", content="You are a helpful assistant."),
                Message(role="user", content="What is 2+2?"),
            ]
        )

        response = client.generate(request)

        assert response is not None
        assert response.content
        assert len(response.content) > 0

    def test_generate_with_model_selection(self):
        """Client can generate with specific model."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model="llama2")

        response = client.generate(request)

        assert response.model == "llama2"

    def test_list_models_returns_list(self):
        """Client can list available models."""
        from llm_client import LLMClient, LLMConfig, ModelInfo

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        models = client.list_models()

        assert isinstance(models, list)
        assert len(models) >= 0  # May be empty if no models installed

        if models:
            assert isinstance(models[0], ModelInfo)
            assert models[0].id
            assert models[0].provider == "ollama"

    def test_list_models_uses_cache(self):
        """Second call to list_models uses cache (faster)."""
        from llm_client import LLMClient, LLMConfig
        import time

        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:11434",
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
        from llm_client import LLMClient, LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
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
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Say 'hi'")])

        response = client.generate(request)

        # Usage may be None for providers that don't support it
        if response.usage:
            assert response.usage.prompt_tokens >= 0
            assert response.usage.completion_tokens >= 0
            assert response.usage.total_tokens >= 0

    def test_response_includes_latency(self):
        """Response includes latency measurement."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        response = client.generate(request)

        assert response.latency_ms > 0


class TestErrorHandlingContracts:
    """Contract tests for error handling behavior."""

    def test_connection_error_when_service_unreachable(self):
        """Client raises ConnectionError when service is unreachable."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message
        from llm_client.exceptions import ConnectionError

        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:9999",  # Non-existent port
            max_retries=0,  # No retries for faster test
        )
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        with pytest.raises(ConnectionError):
            client.generate(request)

    def test_validation_error_on_empty_messages(self):
        """Client raises ValidationError for empty message list."""
        from llm_client import LLMRequest
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(messages=[])

    def test_validation_error_on_invalid_temperature(self):
        """Client raises ValidationError for invalid temperature."""
        from llm_client import LLMRequest, Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(
                messages=[Message(role="user", content="Hello")],
                temperature=3.0,  # Out of range
            )

    def test_timeout_error_on_slow_response(self):
        """Client raises TimeoutError when request exceeds timeout."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message
        from llm_client.exceptions import TimeoutError

        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:11434",
            timeout=0.001,  # Very short timeout
        )
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        with pytest.raises(TimeoutError):
            client.generate(request)


class TestRetryAndFallbackContracts:
    """Contract tests for retry and fallback behavior."""

    def test_retry_on_transient_failure(self):
        """Client retries on transient failures."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", max_retries=3)
        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        response = client.generate(request)

        # If request succeeded after retries
        assert response.retry_count >= 0

    def test_fallback_to_secondary_provider(self):
        """Client falls back to secondary provider on primary failure."""
        from llm_client import LLMClient, LLMConfig, LLMRequest, Message

        fallback_config = LLMConfig(provider="lmstudio", base_url="http://localhost:1234")

        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:9999",  # Non-existent
            max_retries=0,
            fallback_configs=[fallback_config],
        )

        client = LLMClient(config)

        request = LLMRequest(messages=[Message(role="user", content="Hello")])

        response = client.generate(request)

        assert response.used_fallback is True
        assert response.fallback_provider == "lmstudio"
