"""JSON rendering helpers for shared formatter interfaces."""

import json
from typing import Any


def serialize_deterministic(payload: Any) -> str:
    """Serialize payload with deterministic key ordering and formatting."""
    return json.dumps(payload, indent=2, sort_keys=True)


def build_json_output(payload: dict[str, Any], include_metadata: bool) -> dict[str, Any]:
    """Build the canonical JSON formatter response object."""
    output = dict(payload)
    metadata = output.pop("metadata", None)
    passthrough = bool(output.pop("_json_passthrough", False))

    if passthrough:
        response = output
        if include_metadata and metadata is not None:
            response["metadata"] = metadata
        return response

    response: dict[str, Any] = {"output": output}
    if include_metadata and metadata is not None:
        response["metadata"] = metadata
    return response
