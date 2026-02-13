"""Metadata normalization helpers for shared formatters."""

from copy import deepcopy
from typing import Any


def normalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize metadata into processing/configuration/source/extensions groups."""
    if metadata is None:
        return None

    raw = deepcopy(metadata)
    processing = deepcopy(raw.get("processing", {}))
    configuration = deepcopy(raw.get("configuration", {}))
    source = deepcopy(raw.get("source", {}))

    extensions = deepcopy(raw.get("extensions", {}))
    for key, value in raw.items():
        if key not in {"processing", "configuration", "source", "extensions"}:
            extensions[key] = value

    return {
        "processing": processing,
        "configuration": configuration,
        "source": source,
        "extensions": extensions,
    }
