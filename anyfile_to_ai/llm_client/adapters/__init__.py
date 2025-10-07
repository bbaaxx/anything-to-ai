"""Adapter factory and registry for LLM providers.

This module provides a factory function to get the appropriate adapter
for a given provider configuration.
"""

from typing import Dict, Type

from anyfile_to_ai.llm_client.adapters.base import BaseAdapter
from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
from anyfile_to_ai.llm_client.adapters.mlx_adapter import MLXAdapter
from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
from anyfile_to_ai.llm_client.config import LLMConfig

# Registry of provider names to adapter classes
ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    "ollama": OllamaAdapter,
    "lmstudio": LMStudioAdapter,
    "mlx": MLXAdapter,
}


def get_adapter(config: LLMConfig) -> BaseAdapter:
    """Get adapter instance for given configuration.

    Args:
        config: LLM configuration specifying provider

    Returns:
        Adapter instance for the specified provider

    Raises:
        ConfigurationError: If provider is not supported
    """
    from anyfile_to_ai.llm_client.exceptions import ConfigurationError

    adapter_class = ADAPTER_REGISTRY.get(config.provider)

    if adapter_class is None:
        available = ", ".join(ADAPTER_REGISTRY.keys()) if ADAPTER_REGISTRY else "none"
        raise ConfigurationError(
            f"Unsupported provider: {config.provider}. Available providers: {available}",
            provider=config.provider,
        )

    return adapter_class(config)


__all__ = [
    "ADAPTER_REGISTRY",
    "BaseAdapter",
    "LMStudioAdapter",
    "MLXAdapter",
    "OllamaAdapter",
    "get_adapter",
]
