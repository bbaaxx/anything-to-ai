"""CLI entry point for document conversion."""

import argparse
import json
import sys
from typing import Any

from .converter import convert_document
from .exceptions import DocumentConversionError
from .models import ConversionResult


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a local file path or HTTP/HTTPS URL to text")
    parser.add_argument("source", help="Source to convert (path or HTTP/HTTPS URL)")
    parser.add_argument("--include-metadata", action="store_true", help="Include metadata for specialized routes")
    return parser


def _serialize_result(result: ConversionResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source": result.source,
        "route": result.route.value,
        "content": result.content,
    }

    if result.metadata is not None:
        payload["metadata"] = result.metadata
    if result.raw_result is not None:
        payload["raw_result"] = repr(result.raw_result)

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        result = convert_document(args.source, include_metadata=args.include_metadata)
    except DocumentConversionError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(_serialize_result(result), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
