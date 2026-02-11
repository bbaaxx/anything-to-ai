"""LM Studio adapter for LLM client.

This adapter provides integration with LM Studio's OpenAI-compatible API with optional authentication.
"""

import base64
import mimetypes
import time
import uuid
from pathlib import Path

import httpx

from anyfile_to_ai.llm_client.adapters.base import BaseAdapter
from anyfile_to_ai.llm_client.exceptions import (
    AuthenticationError,
    ConnectionError,
    GenerationError,
    TimeoutError,
)
from anyfile_to_ai.llm_client.models import LLMRequest, LLMResponse, ModelInfo, Usage, VisionRequest, VisionResponse


class LMStudioAdapter(BaseAdapter):
    """Adapter for LM Studio LLM service."""

    def _normalize_base_url(self) -> str:
        base_url = self.config.base_url.rstrip("/")
        if base_url.endswith("/v1"):
            return base_url[:-3]
        return base_url

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers including authentication if configured.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {"Content-Type": "application/json"}

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers

    def _resolve_model(self, request_model: str | None) -> str | None:
        """Resolve model name, falling back to first available when missing."""
        if request_model:
            return request_model

        try:
            models = self.list_models()
        except Exception:
            return None

        if models:
            return models[0].id
        return None

    def _encode_image(self, request: VisionRequest) -> tuple[str, str]:
        """Encode image data for OpenAI-style multimodal requests."""
        if request.image_path:
            image_path = Path(request.image_path)
            if not image_path.exists():
                msg = f"Image file not found: {request.image_path}"
                raise GenerationError(msg, provider="lmstudio")
            image_bytes = image_path.read_bytes()
            mime_type = request.image_mime_type or mimetypes.guess_type(str(image_path))[0] or "image/png"
        else:
            image_bytes = request.image_bytes
            mime_type = request.image_mime_type or "image/png"

        if not image_bytes:
            msg = "Image data is empty"
            raise GenerationError(msg, provider="lmstudio")

        encoded = base64.b64encode(image_bytes).decode("ascii")
        return mime_type, encoded

    def _is_vision_compatibility_error(self, response_text: str) -> bool:
        normalized = response_text.lower()
        return "speculativedecodingnotsupportederror" in normalized or "model has crashed" in normalized

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
        base_url = self._normalize_base_url()
        url = f"{base_url}/v1/chat/completions"
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
                    msg = "Invalid or missing API key"
                    raise AuthenticationError(msg, provider="lmstudio")

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
            msg = f"Request to LM Studio timed out after {timeout}s"
            raise TimeoutError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except httpx.ConnectError as e:
            msg = f"Failed to connect to LM Studio at {self.config.base_url}"
            raise ConnectionError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except httpx.HTTPStatusError as e:
            msg = f"LM Studio returned error: {e.response.status_code} - {e.response.text}"
            raise GenerationError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except Exception as e:
            msg = f"Unexpected error during generation: {e}"
            raise GenerationError(
                msg,
                provider="lmstudio",
                original_error=e,
            )

    def generate_vision(self, request: VisionRequest) -> VisionResponse:
        """Generate completion using LM Studio's OpenAI-compatible vision API."""
        base_url = self._normalize_base_url()
        url = f"{base_url}/v1/chat/completions"
        timeout = request.timeout_override if request.timeout_override else self.config.timeout

        resolved_model = self._resolve_model(request.model)
        if not resolved_model:
            msg = "No model specified and no models available from LM Studio"
            raise GenerationError(msg, provider="lmstudio")

        mime_type, encoded = self._encode_image(request)
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}},
                    ],
                },
            ],
            "temperature": request.temperature,
            "stream": False,
        }

        payload["model"] = resolved_model

        # Keep optional generation controls when available.
        # A minimal compatibility retry is attempted below for LM Studio runtimes
        # that reject these controls for specific vision models.
        compatibility_payload = {
            "model": resolved_model,
            "messages": payload["messages"],
            "stream": False,
        }

        used_compatibility_retry = False
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        start_time = time.time()

        try:
            with httpx.Client(timeout=timeout, verify=self.config.verify_ssl) as client:
                response = client.post(url, json=payload, headers=self._get_headers())

                if response.status_code == 401:
                    msg = "Invalid or missing API key"
                    raise AuthenticationError(msg, provider="lmstudio")

                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    response_text = response.text
                    if "No models loaded" in response_text:
                        retry_model = self._resolve_model(resolved_model)
                        if retry_model and retry_model != resolved_model:
                            payload["model"] = retry_model
                            response = client.post(url, json=payload, headers=self._get_headers())
                            response.raise_for_status()
                            data = response.json()
                        else:
                            raise
                    elif self._is_vision_compatibility_error(response_text) and not used_compatibility_retry:
                        used_compatibility_retry = True
                        response = client.post(url, json=compatibility_payload, headers=self._get_headers())
                        response.raise_for_status()
                        data = response.json()
                    else:
                        raise
                else:
                    data = response.json()

            latency_ms = (time.time() - start_time) * 1000

            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")

            usage = None
            if "usage" in data:
                usage = Usage(
                    prompt_tokens=data["usage"]["prompt_tokens"],
                    completion_tokens=data["usage"]["completion_tokens"],
                    total_tokens=data["usage"]["total_tokens"],
                )

            return VisionResponse(
                content=content,
                model=data.get("model", resolved_model or "unknown"),
                finish_reason=finish_reason,
                response_id=data.get("id", str(uuid.uuid4())),
                provider="lmstudio",
                latency_ms=latency_ms,
                usage=usage,
            )

        except AuthenticationError:
            raise
        except httpx.TimeoutException as e:
            msg = f"Request to LM Studio timed out after {timeout}s"
            raise TimeoutError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except httpx.ConnectError as e:
            msg = f"Failed to connect to LM Studio at {self.config.base_url}"
            raise ConnectionError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except httpx.HTTPStatusError as e:
            msg = f"LM Studio returned error: {e.response.status_code} - {e.response.text}"
            raise GenerationError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except Exception as e:
            msg = f"Unexpected error during generation: {e}"
            raise GenerationError(
                msg,
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
        base_url = self._normalize_base_url()
        url = f"{base_url}/v1/models"

        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code == 401:
                    msg = "Invalid or missing API key"
                    raise AuthenticationError(msg, provider="lmstudio")

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
            msg = f"Failed to connect to LM Studio at {self.config.base_url}"
            raise ConnectionError(
                msg,
                provider="lmstudio",
                original_error=e,
            )
        except Exception as e:
            msg = f"Failed to list models: {e}"
            raise ConnectionError(msg, provider="lmstudio", original_error=e)

    def health_check(self) -> bool:
        """Check if LM Studio service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
        base_url = self._normalize_base_url()
        url = f"{base_url}/v1/models"

        try:
            with httpx.Client(timeout=5.0, verify=self.config.verify_ssl) as client:
                response = client.get(url, headers=self._get_headers())
                return response.status_code == 200
        except Exception:
            return False
