---
description: Run the complete testing pipeline
---

# Testing Pipeline

This command runs the complete testing pipeline for the project.

## Prerequisites

Before running tests:

1. **Install dependencies**: `uv sync`
2. **For VLM tests**: `uv pip install mlx-vlm` (first run downloads model files ~5 min)
3. **For LLM client tests**: Ollama (port 11434) or LM Studio (port 1234) running

## Quick Start

```bash
# Run unit tests only (fastest, no VLM required)
uv run pytest tests/unit -q

# Run full pipeline with VLM support
VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit" uv run ruff check . && uv run ruff format . --check && uv run pytest
```

## Step-by-Step Pipeline

1. Run `uv run ruff check .` - check for lint errors
2. Run `uv run ruff format . --check` - verify code formatting  
3. Run `uv run pytest` - execute tests
4. Report any failures
5. Fix failures and repeat until all pass

## Test Commands

### Unit Tests (No VLM Required)
```bash
uv run pytest tests/unit -q
```

### Contract Tests (Excludes Slow LLM/VLM Tests)
```bash
uv run pytest tests/contract -k "not (llm_client or adapter or process_image or process_images)" -q
```

### Full Test Suite (Requires VLM)
```bash
VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit" VLM_TIMEOUT_SECONDS=300 uv run pytest -q
```

### VLM Integration Tests
```bash
# Single image tests
VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit" VLM_TIMEOUT_SECONDS=300 uv run pytest tests/contract/test_api_process_image.py -v

# Batch image tests
VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit" VLM_TIMEOUT_SECONDS=600 uv run pytest tests/contract/test_api_process_images.py -v
```

### Fast Test Iteration
```bash
./run_tests_fast.sh tests/unit/test_chunker.py
```

### Coverage Report
```bash
./run_coverage.sh
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VISION_MODEL` | `mlx-community/GLM-4.6V-Flash-4bit` | VLM model for image processing |
| `VLM_TIMEOUT_SECONDS` | `60` | Timeout for VLM inference |
| `PROVIDER` | - | LLM provider (ollama, lmstudio) |
| `BASE_URL` | - | Base URL for LLM provider |

## Common Issues

- **"VISION_MODEL not set"**: Set `VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit"` or let it use default
- **Model download timeout**: First VLM test downloads model files (~5 min). Use `VLM_TIMEOUT_SECONDS=600`
- **Import errors**: Run `uv sync` to install dependencies
- **Missing mlx-vlm**: Run `uv pip install mlx-vlm` for VLM support
- **LLM client tests fail**: Ensure Ollama/LM Studio is running on ports 11434/1234