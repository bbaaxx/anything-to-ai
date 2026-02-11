"""Shared provider/env helpers for provider-configurable tests."""

from __future__ import annotations

import importlib.util
import os
from typing import Iterable

DEFAULT_PROVIDER = "ollama"
DEFAULT_BASE_URLS = {
    "ollama": "http://localhost:11434",
    "lmstudio": "http://localhost:1234",
}
DEFAULT_VISION_MODEL = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
TEXT_PROVIDERS = {"ollama", "lmstudio"}
VISION_PROVIDERS = {"ollama", "lmstudio", "mlx"}


def normalize_base_url(url: str | None) -> str | None:
    if not url:
        return url
    normalized = url.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized[:-3]
    return normalized


def env_provider() -> str | None:
    provider = os.environ.get("PROVIDER")
    if not provider:
        return None
    return provider.strip().lower()


def provider_mismatch_reason(expected_provider: str) -> str | None:
    provider = env_provider()
    if provider and provider != expected_provider:
        return f"PROVIDER is set to '{provider}', expected '{expected_provider}'"
    return None


def resolve_base_url(expected_provider: str, default_base_url: str) -> str:
    provider = env_provider()
    if provider == expected_provider:
        base_url = os.environ.get("BASE_URL") or default_base_url
    elif provider:
        base_url = default_base_url
    else:
        base_url = default_base_url
    return normalize_base_url(base_url) or default_base_url


def resolve_text_provider(default_provider: str = DEFAULT_PROVIDER) -> tuple[str | None, str | None, str | None, str | None]:
    provider = env_provider() or default_provider
    if provider not in TEXT_PROVIDERS:
        return None, None, None, f"PROVIDER '{provider}' does not support text integration tests"
    base_url = os.environ.get("BASE_URL") or DEFAULT_BASE_URLS.get(provider)
    if not base_url:
        return None, None, None, f"BASE_URL required for provider '{provider}'"
    return provider, normalize_base_url(base_url), os.environ.get("TEXT_MODEL"), None


def resolve_vision_model(default: str | None = None, ignore_defaulted: bool = False) -> str | None:
    model = os.environ.get("VISION_MODEL")
    if ignore_defaulted and os.environ.get("VISION_MODEL_DEFAULTED"):
        model = None
    return model or default


def resolve_text_model(default: str | None = None) -> str | None:
    return os.environ.get("TEXT_MODEL") or default


def default_vision_model() -> str:
    return DEFAULT_VISION_MODEL


def mlx_available() -> bool:
    return importlib.util.find_spec("mlx_vlm") is not None


def _httpx_get(url: str, timeout: float = 5.0):
    import httpx

    return httpx.get(url, timeout=timeout)


def check_ollama_available(base_url: str) -> bool:
    try:
        response = _httpx_get(f"{normalize_base_url(base_url)}/api/tags")
        return response.status_code == 200
    except Exception:
        return False


def check_lmstudio_available(base_url: str) -> bool:
    try:
        response = _httpx_get(f"{normalize_base_url(base_url)}/v1/models")
        return response.status_code in {200, 401}
    except Exception:
        return False


def list_openai_models(base_url: str) -> list[str]:
    try:
        response = _httpx_get(f"{normalize_base_url(base_url)}/v1/models")
        if response.status_code != 200:
            return []
        payload = response.json()
        return [model.get("id") for model in payload.get("data", []) if model.get("id")]
    except Exception:
        return []


def check_openai_models(base_url: str) -> bool:
    return len(list_openai_models(base_url)) > 0


def ensure_provider_available(provider: str, base_url: str) -> bool:
    if provider == "ollama":
        return check_ollama_available(base_url)
    if provider == "lmstudio":
        return check_lmstudio_available(base_url)
    if provider == "mlx":
        return mlx_available()
    return False


def normalize_model_choice(models: Iterable[str], requested: str | None) -> str | None:
    model_list = list(models)
    if not model_list:
        return None
    if requested:
        return requested if requested in model_list else None
    return model_list[0]


def generation_skip_reason(error: Exception, provider: str) -> str | None:
    """Return a pytest skip reason for known provider/runtime constraints."""
    message = str(error)

    if "SpeculativeDecodingNotSupportedError" in message:
        return "LM Studio runtime has speculative decoding enabled but active model does not support it"

    if "does not support chat" in message:
        return "Selected Ollama model does not support chat completions"

    if "model" in message.lower() and "not found" in message.lower():
        return "Requested model is not available in the active provider runtime"

    if "no models loaded" in message.lower():
        return "Provider runtime has no loaded models"

    if provider == "lmstudio" and "model has crashed" in message.lower():
        return "LM Studio model crashed while serving request"

    return None
