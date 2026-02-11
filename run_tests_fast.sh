#!/usr/bin/env bash
set -euo pipefail

# Fast local loop: disable coverage instrumentation configured in pyproject addopts.
exec uv run pytest --no-cov "$@"
