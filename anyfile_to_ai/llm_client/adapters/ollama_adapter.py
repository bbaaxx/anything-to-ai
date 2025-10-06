"""Ollama adapter for LLM client.

This adapter provides integration with Ollama's OpenAI-compatible API.
"""

import time
import uuid
from typing import List

import httpx

from anyfile_to_ai.llm_client.adapters.base import BaseAdapter
from anyfile_to_ai.llm_client.exceptions import ConnectionError, GenerationError, TimeoutError
from anyfile_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo, Usage


class OllamaAdapter(BaseAdapter):
    """Adapter for Ollama LLM service."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using Ollama's OpenAI-compatible API.

        Args:
            request: LLM request with messages and parameters

        Returns:
            LLM response with generated content

        Raises:
            ConnectionError: If Ollama service is unreachable
            TimeoutError: If request times out
            GenerationError: If generation fails
        """
        url = f"{self.config.base_url}/v1/chat/completions"
        timeout = request.timeout_override if request.timeout_override else self.config.timeout

        # Build request payload
        payload = {"messages": [{"role": msg.role, "content": msg.content} for msg in request.messages], "temperature": request.temperature, "stream": False}

        if request.model:
            payload["model"] = request.model

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        start_time = time.time()

        try:
            with httpx.Client(timeout=timeout, verify=self.config.verify_ssl) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            latency_ms = (time.time() - start_time) * 1000

            # Parse OpenAI-format response
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")

            # Parse usage statistics
            usage = None
            if "usage" in data:
                usage = Usage(prompt_tokens=data["usage"]["prompt_tokens"], completion_tokens=data["usage"]["completion_tokens"], total_tokens=data["usage"]["total_tokens"])

            return LLMResponse(
                content=content,
                model=data.get("model", request.model or "unknown"),
                finish_reason=finish_reason,
                response_id=data.get("id", str(uuid.uuid4())),
                provider="ollama",
                latency_ms=latency_ms,
                usage=usage,
            )

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request to Ollama timed out after {timeout}s", provider="ollama", original_error=e)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.config.base_url}", provider="ollama", original_error=e)
        except httpx.HTTPStatusError as e:
            raise GenerationError(f"Ollama returned error: {e.response.status_code} - {e.response.text}", provider="ollama", original_error=e)
        except Exception as e:
            raise GenerationError(f"Unexpected error during generation: {e}", provider="ollama", original_error=e)

    def list_models(self) -> List[ModelInfo]:
        """List available models from Ollama.

        Returns:
            List of available models

        Raises:
            ConnectionError: If Ollama service is unreachable
        """
        url = f"{self.config.base_url}/v1/models"

        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()

            models = []
            for model_data in data.get("data", []):
                models.append(
                    ModelInfo(
                        id=model_data["id"],
                        provider="ollama",
                        object=model_data.get("object", "model"),
                        created=model_data.get("created"),
                        owned_by=model_data.get("owned_by"),
                    )
                )

            return models

        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.config.base_url}", provider="ollama", original_error=e)
        except Exception as e:
            raise ConnectionError(f"Failed to list models: {e}", provider="ollama", original_error=e)

    def health_check(self) -> bool:
        """Check if Ollama service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
        # Ollama has a specific health check endpoint
        url = f"{self.config.base_url}/api/tags"

        try:
            with httpx.Client(timeout=5.0, verify=self.config.verify_ssl) as client:
                response = client.get(url)
                return response.status_code == 200
        except Exception:
            return False
