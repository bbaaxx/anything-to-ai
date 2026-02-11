"""Unit tests for vision adapter payloads."""


class DummyResponse:
    """Minimal httpx response stand-in."""

    def __init__(self, payload: dict):
        self.status_code = 200
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class TestVisionAdapterPayloads:
    """Validate payload shape for vision adapters."""

    def test_lmstudio_vision_payload_structure(self, monkeypatch):
        """LM Studio vision requests should be OpenAI-style with image_url."""
        from anyfile_to_ai.llm_client import LLMConfig
        from anyfile_to_ai.llm_client.adapters.lmstudio_adapter import LMStudioAdapter
        from anyfile_to_ai.llm_client.models import VisionRequest
        import httpx

        calls: list[dict] = []

        class DummyClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def post(self, url, json=None, headers=None):
                calls.append({"url": url, "json": json, "headers": headers})
                return DummyResponse(
                    {
                        "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                        "model": "vision-model",
                        "id": "resp-1",
                    },
                )

        monkeypatch.setattr(httpx, "Client", DummyClient)

        adapter = LMStudioAdapter(LLMConfig(provider="lmstudio", base_url="http://localhost:1234"))
        request = VisionRequest(
            prompt="Describe this image.",
            image_bytes=b"fake-image",
            image_mime_type="image/png",
            model="vision-model",
        )

        response = adapter.generate_vision(request)

        assert response.content == "ok"
        assert len(calls) == 1

        payload = calls[0]["json"]
        content = payload["messages"][0]["content"]
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
        assert payload["model"] == "vision-model"

    def test_ollama_vision_payload_structure(self, monkeypatch):
        """Ollama vision requests should be OpenAI-style with image_url."""
        from anyfile_to_ai.llm_client import LLMConfig
        from anyfile_to_ai.llm_client.adapters.ollama_adapter import OllamaAdapter
        from anyfile_to_ai.llm_client.models import VisionRequest
        import httpx

        calls: list[dict] = []

        class DummyClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def post(self, url, json=None):
                calls.append({"url": url, "json": json})
                return DummyResponse(
                    {
                        "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                        "model": "vision-model",
                        "id": "resp-2",
                    },
                )

        monkeypatch.setattr(httpx, "Client", DummyClient)

        adapter = OllamaAdapter(LLMConfig(provider="ollama", base_url="http://localhost:11434"))
        request = VisionRequest(
            prompt="Describe this image.",
            image_bytes=b"fake-image",
            image_mime_type="image/png",
            model="vision-model",
        )

        response = adapter.generate_vision(request)

        assert response.content == "ok"
        assert len(calls) == 1

        payload = calls[0]["json"]
        content = payload["messages"][0]["content"]
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
        assert payload["model"] == "vision-model"
