"""Shared CLI/provider configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any


@dataclass(frozen=True)
class ProviderConfig:
    """Resolved provider configuration values."""

    provider: str | None
    base_url: str | None
    text_model: str | None
    vision_model: str | None


class ProviderConfigError(ValueError):
    """Raised when required provider configuration is missing."""

    def __init__(self, missing_keys: list[str]):
        self.missing_keys = missing_keys
        msg = f"Missing required configuration: {', '.join(missing_keys)}"
        super().__init__(msg)


def resolve_provider_config(
    cli_args: Any,
    *,
    text_model_alias: str | None = None,
    require_text: bool = False,
    require_vision: bool = False,
    provider_default: str | None = None,
    text_default: str | None = None,
    vision_default: str | None = None,
) -> ProviderConfig:
    """Resolve provider config from CLI args, env, and defaults.

    Resolution order:
        1) CLI flags
        2) Env vars
        3) Defaults

    Env vars:
        PROVIDER, BASE_URL, TEXT_MODEL, VISION_MODEL
    """

    def _get_attr(name: str) -> Any:
        return getattr(cli_args, name) if hasattr(cli_args, name) else None

    provider_cli = _get_attr("provider")
    base_url_cli = _get_attr("base_url")
    text_model_cli = _get_attr("text_model")
    vision_model_cli = _get_attr("vision_model")

    text_alias_value = None
    if not text_model_cli and text_model_alias:
        text_alias_value = _get_attr(text_model_alias)

    provider = provider_cli or os.getenv("PROVIDER") or provider_default
    base_url = base_url_cli or os.getenv("BASE_URL")
    text_model = text_model_cli or text_alias_value or os.getenv("TEXT_MODEL") or text_default
    vision_model = vision_model_cli or os.getenv("VISION_MODEL") or vision_default

    if provider_cli:
        os.environ["PROVIDER"] = provider_cli
    if base_url_cli:
        os.environ["BASE_URL"] = base_url_cli
    if text_model_cli:
        os.environ["TEXT_MODEL"] = text_model_cli
    elif text_alias_value:
        os.environ["TEXT_MODEL"] = text_alias_value
    if vision_model_cli:
        os.environ["VISION_MODEL"] = vision_model_cli

    missing_keys = []
    if require_text and not text_model:
        missing_keys.append("TEXT_MODEL")
    if require_vision and not vision_model:
        missing_keys.append("VISION_MODEL")

    if missing_keys:
        raise ProviderConfigError(missing_keys)

    return ProviderConfig(
        provider=provider,
        base_url=base_url,
        text_model=text_model,
        vision_model=vision_model,
    )
