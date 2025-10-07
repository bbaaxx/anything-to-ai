"""LM Studio adapter for LLM client.

This adapter provides integration with LM Studio's OpenAI-compatible API with optional authentication.
"""

import time
import uuid

import httpx

from anything_to_ai.llm_client.adapters.base import BaseAdapter
from anything_to_ai.llm_client.exceptions import (
    AuthenticationError,
    ConnectionError,
    GenerationError,
    TimeoutError,
)
from anything_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo, Usage


class LMStudioAdapter(BaseAdapter):
    """Adapter for LM Studio LLM service."""

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers including authentication if configured.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {"Content-Type": "application/json"}

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using LM Studio's OpenAI-compatible API.

        Args:
            request: LLM request with messages and parameters

        Returns:
            LLM response with generated content

        Raises:
            ConnectionError: If LM Studio service is unreachable
            AuthenticationError: If API key is invalid
            TimeoutError: If request times out
            GenerationError: If generation fails
        """
        url = f"{self.config.base_url}/v1/chat/completions"
        timeout = request.timeout_override if request.timeout_override else self.config.timeout

        # Build request payload
        payload = {
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }

        if request.model:
            payload["model"] = request.model

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        start_time = time.time()

        try:
            with httpx.Client(timeout=timeout, verify=self.config.verify_ssl) as client:
                response = client.post(url, json=payload, headers=self._get_headers())

                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid or missing API key", provider="lmstudio")

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
                usage = Usage(
                    prompt_tokens=data["usage"]["prompt_tokens"],
                    completion_tokens=data["usage"]["completion_tokens"],
                    total_tokens=data["usage"]["total_tokens"],
                )

            return LLMResponse(
                content=content,
                model=data.get("model", request.model or "unknown"),
                finish_reason=finish_reason,
                response_id=data.get("id", str(uuid.uuid4())),
                provider="lmstudio",
                latency_ms=latency_ms,
                usage=usage,
            )

        except AuthenticationError:
            raise
        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request to LM Studio timed out after {timeout}s",
                provider="lmstudio",
                original_error=e,
            )
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio at {self.config.base_url}",
                provider="lmstudio",
                original_error=e,
            )
        except httpx.HTTPStatusError as e:
            raise GenerationError(
                f"LM Studio returned error: {e.response.status_code} - {e.response.text}",
                provider="lmstudio",
                original_error=e,
            )
        except Exception as e:
            raise GenerationError(
                f"Unexpected error during generation: {e}",
                provider="lmstudio",
                original_error=e,
            )

    def list_models(self) -> list[ModelInfo]:
        """List available models from LM Studio.

        Returns:
            List of available models

        Raises:
            ConnectionError: If LM Studio service is unreachable
            AuthenticationError: If API key is invalid
        """
        url = f"{self.config.base_url}/v1/models"

        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or missing API key", provider="lmstudio")

                response.raise_for_status()
                data = response.json()

            models = []
            for model_data in data.get("data", []):
                models.append(
                    ModelInfo(
                        id=model_data["id"],
                        provider="lmstudio",
                        object=model_data.get("object", "model"),
                        created=model_data.get("created"),
                        owned_by=model_data.get("owned_by"),
                    ),
                )

            return models

        except AuthenticationError:
            raise
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio at {self.config.base_url}",
                provider="lmstudio",
                original_error=e,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to list models: {e}", provider="lmstudio", original_error=e)

    def health_check(self) -> bool:
        """Check if LM Studio service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
        url = f"{self.config.base_url}/v1/models"

        try:
            with httpx.Client(timeout=5.0, verify=self.config.verify_ssl) as client:
                response = client.get(url, headers=self._get_headers())
                return response.status_code == 200
        except Exception:
            return False
