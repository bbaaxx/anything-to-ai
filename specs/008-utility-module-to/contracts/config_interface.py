"""Contract tests for configuration interface.

These tests define the expected behavior of LLMConfig and related configuration.
All tests should FAIL until implementation is complete.
"""

import pytest


class TestLLMConfigCreation:
    """Contract tests for LLMConfig creation and validation."""

    def test_create_minimal_config(self):
        """Config can be created with minimal required fields."""
        from llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434")

        assert config.provider == "ollama"
        assert config.base_url == "http://localhost:11434"
        assert config.api_key is None
        assert config.timeout == 30.0  # Default

    def test_create_config_with_all_fields(self):
        """Config can be created with all fields specified."""
        from llm_client import LLMConfig

        config = LLMConfig(provider="lmstudio", base_url="http://localhost:1234", api_key="test-key", timeout=60.0, verify_ssl=False, max_retries=5, retry_delay=2.0, retry_max_delay=20.0, retry_exponential_base=3.0, cache_ttl=600)

        assert config.provider == "lmstudio"
        assert config.api_key == "test-key"
        assert config.timeout == 60.0
        assert config.verify_ssl is False
        assert config.max_retries == 5
        assert config.cache_ttl == 600

    def test_config_is_immutable(self):
        """LLMConfig is frozen/immutable after creation."""
        from llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost")

        # Should not be able to modify
        with pytest.raises((AttributeError, TypeError)):
            config.provider = "lmstudio"

    def test_config_validates_provider(self):
        """Config validates provider is one of supported values."""
        from llm_client import LLMConfig
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMConfig(provider="unsupported", base_url="http://localhost")

    def test_config_validates_base_url(self):
        """Config validates base_url is valid URL format."""
        from llm_client import LLMConfig
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMConfig(provider="ollama", base_url="not-a-url")

    def test_config_validates_timeout(self):
        """Config validates timeout is positive."""
        from llm_client import LLMConfig
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMConfig(provider="ollama", base_url="http://localhost", timeout=-1.0)

    def test_config_validates_max_retries(self):
        """Config validates max_retries is non-negative."""
        from llm_client import LLMConfig
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMConfig(provider="ollama", base_url="http://localhost", max_retries=-1)

    def test_config_validates_cache_ttl(self):
        """Config validates cache_ttl is non-negative."""
        from llm_client import LLMConfig
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMConfig(provider="ollama", base_url="http://localhost", cache_ttl=-10)


class TestLLMConfigFallback:
    """Contract tests for fallback configuration."""

    def test_config_accepts_fallback_list(self):
        """Config accepts list of fallback configs."""
        from llm_client import LLMConfig

        fallback1 = LLMConfig(provider="lmstudio", base_url="http://localhost:1234")
        fallback2 = LLMConfig(provider="mlx", base_url="local")

        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", fallback_configs=[fallback1, fallback2])

        assert len(config.fallback_configs) == 2
        assert config.fallback_configs[0].provider == "lmstudio"
        assert config.fallback_configs[1].provider == "mlx"

    def test_config_fallback_is_optional(self):
        """Fallback configs are optional (None by default)."""
        from llm_client import LLMConfig

        config = LLMConfig(provider="ollama", base_url="http://localhost")

        assert config.fallback_configs is None or config.fallback_configs == []


class TestMessageModel:
    """Contract tests for Message model."""

    def test_create_message_with_role_and_content(self):
        """Message can be created with role and content."""
        from llm_client import Message

        msg = Message(role="user", content="Hello, world!")

        assert msg.role == "user"
        assert msg.content == "Hello, world!"

    def test_message_validates_role(self):
        """Message validates role is valid."""
        from llm_client import Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            Message(role="invalid_role", content="Hello")

    def test_message_validates_content_not_empty(self):
        """Message validates content is not empty."""
        from llm_client import Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            Message(role="user", content="")

    def test_message_is_immutable(self):
        """Message is frozen/immutable after creation."""
        from llm_client import Message

        msg = Message(role="user", content="Hello")

        with pytest.raises((AttributeError, TypeError)):
            msg.content = "Changed"


class TestLLMRequestModel:
    """Contract tests for LLMRequest model."""

    def test_create_request_with_messages(self):
        """LLMRequest can be created with message list."""
        from llm_client import LLMRequest, Message

        request = LLMRequest(messages=[Message(role="system", content="You are helpful."), Message(role="user", content="Hello!")])

        assert len(request.messages) == 2
        assert request.temperature == 0.7  # Default

    def test_request_validates_messages_not_empty(self):
        """LLMRequest validates messages list is not empty."""
        from llm_client import LLMRequest
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(messages=[])

    def test_request_validates_temperature_range(self):
        """LLMRequest validates temperature is in valid range."""
        from llm_client import LLMRequest, Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(
                messages=[Message(role="user", content="Hi")],
                temperature=3.0,  # Out of range
            )

    def test_request_validates_max_tokens_positive(self):
        """LLMRequest validates max_tokens is positive if provided."""
        from llm_client import LLMRequest, Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(messages=[Message(role="user", content="Hi")], max_tokens=0)

    def test_request_requires_user_message(self):
        """LLMRequest validates at least one user message exists."""
        from llm_client import LLMRequest, Message
        from llm_client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            LLMRequest(messages=[Message(role="system", content="System prompt only")])


class TestLLMResponseModel:
    """Contract tests for LLMResponse model."""

    def test_response_has_required_fields(self):
        """LLMResponse has all required fields."""
        from llm_client import LLMResponse

        response = LLMResponse(content="Generated text", model="llama2", finish_reason="stop", response_id="resp-123", provider="ollama", latency_ms=125.5)

        assert response.content == "Generated text"
        assert response.model == "llama2"
        assert response.finish_reason == "stop"
        assert response.provider == "ollama"
        assert response.latency_ms == 125.5

    def test_response_is_immutable(self):
        """LLMResponse is frozen/immutable."""
        from llm_client import LLMResponse

        response = LLMResponse(content="Text", model="llama2", finish_reason="stop", response_id="resp-123", provider="ollama", latency_ms=100.0)

        with pytest.raises((AttributeError, TypeError)):
            response.content = "Changed"

    def test_response_tracks_retry_info(self):
        """LLMResponse tracks retry and fallback information."""
        from llm_client import LLMResponse

        response = LLMResponse(content="Text", model="llama2", finish_reason="stop", response_id="resp-123", provider="lmstudio", latency_ms=100.0, retry_count=2, used_fallback=True, fallback_provider="lmstudio")

        assert response.retry_count == 2
        assert response.used_fallback is True
        assert response.fallback_provider == "lmstudio"


class TestModelInfoModel:
    """Contract tests for ModelInfo model."""

    def test_modelinfo_has_required_fields(self):
        """ModelInfo has required fields."""
        from llm_client import ModelInfo

        info = ModelInfo(id="llama2", provider="ollama")

        assert info.id == "llama2"
        assert info.provider == "ollama"
        assert info.object == "model"  # Default

    def test_modelinfo_supports_extended_metadata(self):
        """ModelInfo supports extended metadata fields."""
        from llm_client import ModelInfo

        info = ModelInfo(id="llama2", provider="ollama", context_length=4096, description="Llama 2 model")

        assert info.context_length == 4096
        assert info.description == "Llama 2 model"
