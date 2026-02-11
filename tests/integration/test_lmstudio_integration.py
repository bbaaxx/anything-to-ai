"""Integration tests for LM Studio provider.

These tests require a running LM Studio service at http://localhost:1234.
Skip if service is unavailable.
"""

import os
import pytest
from anyfile_to_ai.llm_client import (
    LLMClient,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    Message,
    ModelInfo,
)
from anyfile_to_ai.llm_client.exceptions import (
    ConnectionError as LLMConnectionError,
    AuthenticationError,
    GenerationError,
)
from provider_env import (
    check_lmstudio_available,
    generation_skip_reason,
    provider_mismatch_reason,
    resolve_base_url,
    resolve_text_model,
)

# Test configuration
LMSTUDIO_BASE_URL = resolve_base_url("lmstudio", "http://localhost:1234")
REQUESTED_TEXT_MODEL = resolve_text_model(os.environ.get("LMSTUDIO_MODEL"))
TEST_TIMEOUT = 30.0


def check_lmstudio_available_for_tests() -> bool:
    """Check if LM Studio service is available."""
    return check_lmstudio_available(LMSTUDIO_BASE_URL)


_SKIP_REASON = provider_mismatch_reason("lmstudio")
if not _SKIP_REASON and not check_lmstudio_available_for_tests():
    _SKIP_REASON = f"LM Studio service not available at {LMSTUDIO_BASE_URL}"

# Skip all tests if LM Studio is not running
pytestmark = pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")


def _select_model(models: list[ModelInfo]) -> str:
    if not models:
        pytest.skip("No models available in LM Studio")
    if REQUESTED_TEXT_MODEL:
        for model in models:
            if model.id == REQUESTED_TEXT_MODEL:
                return model.id
        pytest.skip(f"TEXT_MODEL not available: {REQUESTED_TEXT_MODEL}")
    return models[0].id


def _generate_or_skip(client: LLMClient, request: LLMRequest):
    try:
        return client.generate(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, "lmstudio")
        if skip_reason:
            pytest.skip(skip_reason)
        raise


@pytest.mark.integration
class TestLMStudioConnection:
    """Test LM Studio service connection."""

    def test_lmstudio_service_reachable(self):
        """Test that LM Studio service is reachable."""
        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, timeout=TEST_TIMEOUT)
        client = LLMClient(config)

        # Should not raise ConnectionError
        # May raise AuthenticationError if auth is required
        try:
            models = client.list_models()
            assert isinstance(models, list)
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

    def test_lmstudio_connection_with_invalid_url(self):
        """Test connection error with invalid URL."""
        config = LLMConfig(
            provider="lmstudio",
            base_url="http://localhost:99999",  # Invalid port
            timeout=2.0,
            max_retries=0,  # Disable retries for faster test
        )
        client = LLMClient(config)

        with pytest.raises(LLMConnectionError):
            client.list_models()


@pytest.mark.integration
class TestLMStudioAuthentication:
    """Test LM Studio authentication."""

    def test_without_api_key(self):
        """Test access without API key (should work if auth is disabled)."""
        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, api_key=None)
        client = LLMClient(config)

        try:
            models = client.list_models()
            assert isinstance(models, list)
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

    def test_with_api_key_from_env(self):
        """Test authentication with API key from environment."""
        api_key = os.environ.get("LMSTUDIO_API_KEY")
        if not api_key:
            pytest.skip("LMSTUDIO_API_KEY not set (optional: only required when LM Studio auth is enabled)")

        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, api_key=api_key)
        client = LLMClient(config)

        models = client.list_models()
        assert isinstance(models, list)


@pytest.mark.integration
class TestLMStudioModelListing:
    """Test LM Studio model listing functionality."""

    def test_list_models_returns_models(self):
        """Test that list_models returns available models."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
            max_retries=0,
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        assert isinstance(models, list)
        if len(models) > 0:
            model = models[0]
            assert isinstance(model, ModelInfo)
            assert model.id
            assert model.provider == "lmstudio"

    def test_list_models_caching(self):
        """Test that model listing uses cache."""
        import time

        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
            cache_ttl=60,
        )
        client = LLMClient(config)

        try:
            # First call
            start = time.time()
            models1 = client.list_models()
            first_call_duration = time.time() - start

            # Second call (cached)
            start = time.time()
            models2 = client.list_models()
            second_call_duration = time.time() - start

            assert models1 == models2
            assert second_call_duration < first_call_duration / 2
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")


@pytest.mark.integration
class TestLMStudioGeneration:
    """Test LM Studio text generation."""

    def test_basic_generation(self):
        """Test basic text generation."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
            max_retries=0,
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        request = LLMRequest(
            messages=[Message(role="user", content="Say 'test' and nothing else.")],
            model=_select_model(models),
            temperature=0.0,
            max_tokens=10,
        )

        response = _generate_or_skip(client, request)

        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.model
        assert response.provider == "lmstudio"
        assert response.latency_ms > 0

    def test_generation_with_specific_model(self):
        """Test generation with specific model selection."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
            max_retries=0,
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        target_model = _select_model(models)

        request = LLMRequest(
            messages=[Message(role="user", content="Hello")],
            model=target_model,
            temperature=0.5,
        )

        response = _generate_or_skip(client, request)

        assert response.content
        assert response.model == target_model

    def test_generation_response_metadata(self):
        """Test that response includes proper metadata."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=_select_model(models))

        response = _generate_or_skip(client, request)

        # Check metadata
        assert response.response_id
        assert response.provider == "lmstudio"
        assert response.latency_ms >= 0
        assert response.retry_count >= 0
        assert isinstance(response.used_fallback, bool)
