"""Base adapter interface for LLM providers.

This module defines the abstract base class that all provider adapters must implement.
"""

from abc import ABC, abstractmethod

from anything_to_ai.llm_client.config import LLMConfig
from anything_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo


class BaseAdapter(ABC):
    """Abstract base adapter for LLM service providers."""

    def __init__(self, config: LLMConfig):
        """Initialize adapter with configuration.

        Args:
            config: LLM configuration for this provider
        """
        self.config = config

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion from LLM.

        Args:
            request: LLM request with messages and parameters

        Returns:
            LLM response with generated content

        Raises:
            ConnectionError: If service is unreachable
            TimeoutError: If request times out
            GenerationError: If generation fails
        """

    @abstractmethod
    def list_models(self) -> list[ModelInfo]:
        """List available models from provider.

        Returns:
            List of available models

        Raises:
            ConnectionError: If service is unreachable
        """

    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
