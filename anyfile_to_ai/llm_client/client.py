"""Main LLM client for unified access to multiple LLM providers.

This module orchestrates adapter selection, retry logic, fallback handling,
and caching for LLM operations.
"""

from anything_to_ai.llm_client.adapters import get_adapter
from anything_to_ai.llm_client.cache import ModelCache
from anything_to_ai.llm_client.config import LLMConfig
from anything_to_ai.llm_client.exceptions import LLMError
from anything_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo
from anything_to_ai.llm_client.retry import RetryHandler


class LLMClient:
    """Unified client for accessing multiple LLM service providers.

    The client provides:
    - Automatic adapter selection based on provider configuration
    - Retry logic with exponential backoff
    - Automatic fallback to alternative providers
    - Model listing with caching
    - Request/response metadata tracking
    """

    def __init__(self, config: LLMConfig):
        """Initialize LLM client.

        Args:
            config: Primary provider configuration with optional fallbacks

        Raises:
            ConfigurationError: If config is invalid or adapter not found
        """
        self.config = config

        # Initialize primary adapter
        self.adapter = get_adapter(config)

        # Initialize fallback adapters if configured
        self.fallback_adapters = []
        if config.fallback_configs:
            for fallback_config in config.fallback_configs:
                try:
                    fallback_adapter = get_adapter(fallback_config)
                    self.fallback_adapters.append((fallback_config, fallback_adapter))
                except Exception:
                    # Skip invalid fallback configs
                    pass

        # Initialize cache for model listings
        self.cache = ModelCache(ttl=config.cache_ttl)

        # Initialize retry handler
        self.retry_handler = RetryHandler(
            max_attempts=config.max_retries,
            base_delay=config.retry_delay,
            max_delay=config.retry_max_delay,
            exponential_base=config.retry_exponential_base,
        )

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using configured LLM provider.

        This method orchestrates:
        - Primary provider request with retry logic
        - Automatic fallback to alternative providers on failure
        - Latency measurement and response metadata

        Args:
            request: LLM request with messages and parameters

        Returns:
            LLM response with generated content and metadata

        Raises:
            LLMError: If all providers fail (including fallbacks)
        """
        # Try primary provider with retry
        try:
            response = self._execute_with_fallback(request)
            return response
        except LLMError:
            # All providers exhausted
            raise

    def _execute_with_fallback(self, request: LLMRequest) -> LLMResponse:
        """Execute request with fallback support.

        Args:
            request: LLM request

        Returns:
            LLM response from successful provider

        Raises:
            LLMError: If all providers fail
        """
        # Try primary adapter
        last_error = None

        result = self.retry_handler.execute_with_retry(lambda: self.adapter.generate(request))

        if result["success"]:
            response = result["result"]
            retry_count = result["attempts"] - 1
            return LLMResponse(
                content=response.content,
                model=response.model,
                finish_reason=response.finish_reason,
                usage=response.usage,
                response_id=response.response_id,
                provider=response.provider,
                latency_ms=response.latency_ms,
                retry_count=retry_count,
                used_fallback=False,
                fallback_provider=None,
            )
        last_error = result["error"]

        # Try fallback adapters
        for fallback_config, fallback_adapter in self.fallback_adapters:
            # Create new retry handler for fallback
            fallback_retry = RetryHandler(
                max_attempts=fallback_config.max_retries,
                base_delay=fallback_config.retry_delay,
                max_delay=fallback_config.retry_max_delay,
                exponential_base=fallback_config.retry_exponential_base,
            )

            result = fallback_retry.execute_with_retry(lambda: fallback_adapter.generate(request))

            if result["success"]:
                response = result["result"]
                retry_count = result["attempts"] - 1
                return LLMResponse(
                    content=response.content,
                    model=response.model,
                    finish_reason=response.finish_reason,
                    usage=response.usage,
                    response_id=response.response_id,
                    provider=response.provider,
                    latency_ms=response.latency_ms,
                    retry_count=retry_count,
                    used_fallback=True,
                    fallback_provider=fallback_config.provider,
                )
            last_error = result["error"]
            continue

        # All providers failed
        raise last_error

    def list_models(self, use_cache: bool = True) -> list[ModelInfo]:
        """List available models from provider.

        Uses caching to minimize API calls. Cache is keyed by provider URL.

        Args:
            use_cache: Whether to use cached results (default: True)

        Returns:
            List of available models

        Raises:
            ConnectionError: If provider is unreachable
        """
        cache_key = f"{self.config.provider}:{self.config.base_url}"

        # Try cache first
        if use_cache:
            cached_models = self.cache.get(cache_key)
            if cached_models is not None:
                return cached_models

        # Fetch from provider
        models = self.adapter.list_models()

        # Store in cache
        if use_cache:
            self.cache.set(cache_key, models)

        return models

    def invalidate_cache(self):
        """Invalidate model listing cache.

        Forces next list_models() call to fetch fresh data from provider.
        """
        cache_key = f"{self.config.provider}:{self.config.base_url}"
        self.cache.invalidate(cache_key)

    def health_check(self) -> bool:
        """Check if primary provider is healthy.

        Returns:
            True if provider is responding, False otherwise
        """
        try:
            return self.adapter.health_check()
        except Exception:
            return False
