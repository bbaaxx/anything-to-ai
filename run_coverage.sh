#!/usr/bin/env bash
set -euo pipefail

# Run full test suite with coverage gate (intentionally separate from fast test loop)
exec uv run pytest --cov=anyfile_to_ai --cov-report=term-missing --cov-report=html --cov-fail-under=80 "$@"
