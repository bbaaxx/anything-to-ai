"""Public entry points for shared formatter usage."""

from typing import Any

from .errors import UnsupportedFormatError
from .json_formatter import build_json_output, serialize_deterministic
from .markdown import render_markdown
from .metadata import normalize_metadata
from .plain import render_plain
from .profiles import validate_profile


def _prepare_payload(payload: dict[str, Any], include_metadata: bool) -> dict[str, Any]:
    prepared = dict(payload)
    metadata = normalize_metadata(prepared.get("metadata"))
    if include_metadata and metadata is not None:
        prepared["metadata"] = metadata
    else:
        prepared.pop("metadata", None)
    return prepared


def format_plain(profile: str, payload: dict[str, Any], include_metadata: bool = False) -> str:
    """Render plain output text for a profile."""
    validate_profile(profile)
    prepared = _prepare_payload(payload, include_metadata)
    return render_plain(profile, prepared)


def format_markdown(profile: str, payload: dict[str, Any], include_metadata: bool = False) -> str:
    """Render markdown output text for a profile."""
    validate_profile(profile)
    prepared = _prepare_payload(payload, include_metadata)
    return render_markdown(profile, prepared)


def format_json(profile: str, payload: dict[str, Any], include_metadata: bool = False) -> str:
    """Render deterministic JSON output for a profile."""
    validate_profile(profile)
    prepared = _prepare_payload(payload, include_metadata)
    response = build_json_output(prepared, include_metadata)
    return serialize_deterministic(response)


def format_output(profile: str, payload: dict[str, Any], output_format: str, include_metadata: bool = False) -> str:
    """Render output for the requested format."""
    if output_format == "plain":
        return format_plain(profile, payload, include_metadata=include_metadata)
    if output_format == "markdown":
        return format_markdown(profile, payload, include_metadata=include_metadata)
    if output_format == "json":
        return format_json(profile, payload, include_metadata=include_metadata)
    raise UnsupportedFormatError(output_format)
