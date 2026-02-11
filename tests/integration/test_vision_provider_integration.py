"""Integration tests for provider-aware vision backends."""

import pytest

from anyfile_to_ai.llm_client.exceptions import GenerationError
from provider_env import (
    check_openai_models,
    generation_skip_reason,
    list_openai_models,
    mlx_available,
    provider_mismatch_reason,
    resolve_base_url,
    resolve_vision_model,
)

LMSTUDIO_BASE_URL = resolve_base_url("lmstudio", "http://localhost:1234")
OLLAMA_BASE_URL = resolve_base_url("ollama", "http://localhost:11434")
VISION_MODEL = resolve_vision_model(ignore_defaulted=True)


@pytest.mark.integration
@pytest.mark.skipif(provider_mismatch_reason("lmstudio") is not None, reason=provider_mismatch_reason("lmstudio") or "")
@pytest.mark.skipif(not VISION_MODEL, reason="VISION_MODEL not set")
@pytest.mark.skipif(not check_openai_models(LMSTUDIO_BASE_URL), reason="LM Studio vision endpoint not available")
def test_lmstudio_vision_generate():
    """LM Studio vision generate works via LLM client."""
    from anyfile_to_ai.llm_client import LLMClient, LLMConfig, VisionRequest

    available_models = list_openai_models(LMSTUDIO_BASE_URL)
    if not available_models:
        pytest.skip("No models loaded in LM Studio")

    model = VISION_MODEL or available_models[0]
    if model not in available_models:
        pytest.skip(f"Requested model not loaded: {model}")

    config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, max_retries=0)
    client = LLMClient(config)

    request = VisionRequest(
        prompt="Describe this image.",
        image_path="sample-data/images/ui-screenshot.png",
        model=model,
        max_tokens=200,
        temperature=0.2,
    )

    try:
        response = client.generate_vision(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, "lmstudio")
        if skip_reason:
            pytest.skip(skip_reason)
        raise

    assert response.content
    assert response.provider == "lmstudio"


@pytest.mark.integration
@pytest.mark.skipif(provider_mismatch_reason("ollama") is not None, reason=provider_mismatch_reason("ollama") or "")
@pytest.mark.skipif(not VISION_MODEL, reason="VISION_MODEL not set")
@pytest.mark.skipif(not check_openai_models(OLLAMA_BASE_URL), reason="Ollama vision endpoint not available")
def test_ollama_vision_generate():
    """Ollama vision generate works via LLM client."""
    from anyfile_to_ai.llm_client import LLMClient, LLMConfig, VisionRequest

    available_models = list_openai_models(OLLAMA_BASE_URL)
    if not available_models:
        pytest.skip("No models available in Ollama OpenAI endpoint")

    model = VISION_MODEL or available_models[0]
    if model not in available_models:
        pytest.skip(f"Requested model not available: {model}")

    config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL, max_retries=0)
    client = LLMClient(config)

    request = VisionRequest(
        prompt="Describe this image.",
        image_path="sample-data/images/ui-screenshot.png",
        model=model,
        max_tokens=200,
        temperature=0.2,
    )

    try:
        response = client.generate_vision(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, "ollama")
        if skip_reason:
            pytest.skip(skip_reason)
        raise

    assert response.content
    assert response.provider == "ollama"


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(provider_mismatch_reason("mlx") is not None, reason=provider_mismatch_reason("mlx") or "")
@pytest.mark.skipif(not VISION_MODEL, reason="VISION_MODEL not set")
@pytest.mark.skipif(not mlx_available(), reason="mlx-vlm dependency not available")
def test_mlx_vision_generate():
    """MLX vision generate works via LLM client."""
    from anyfile_to_ai.llm_client import LLMClient, LLMConfig, VisionRequest

    config = LLMConfig(provider="mlx", base_url="local")
    client = LLMClient(config)

    request = VisionRequest(
        prompt="Describe this image.",
        image_path="sample-data/images/ui-screenshot.png",
        model=VISION_MODEL,
        max_tokens=200,
        temperature=0.2,
    )

    response = client.generate_vision(request)

    assert response.content
    assert response.provider == "mlx"
