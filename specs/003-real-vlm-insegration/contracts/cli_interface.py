"""
API Contract: Command Line Interface
Defines the CLI behavior that must be maintained for backward compatibility.
"""

import argparse


def create_cli_parser() -> "argparse.ArgumentParser":
    """
    Create command-line argument parser.

    BACKWARD COMPATIBILITY: Exact same signature and behavior.
    ENHANCEMENT: Parser now supports VLM model environment variable.

    Returns:
        ArgumentParser: CLI argument parser with VLM support

    CLI Usage (Unchanged):
        python -m image_processor image.jpg
        python -m image_processor *.png --style brief
        python -m image_processor folder/ --batch-size 2 --output results.json

    Environment Variables (New):
        VISION_MODEL: VLM model to use (required)

    Examples with VLM:
        export VISION_MODEL=google/gemma-3-4b
        python -m image_processor image.jpg --format json
    """


def main(args: list[str] | None = None) -> int:
    """
    Main CLI entry point.

    BACKWARD COMPATIBILITY: Exact same signature and return behavior.
    ENHANCEMENT: Uses real VLM processing instead of mock.

    Args:
        args: Command line arguments (for testing)

    Returns:
        int: Exit code (0 for success, 1 for error)

    Error Handling (Enhanced):
        - Returns 1 if VISION_MODEL not configured
        - Returns 1 if VLM model fails to load
        - Returns 1 if VLM processing fails
        - Preserves all existing error handling behavior
    """


# CLI Argument Contract (Preserved Exactly)
CLI_ARGUMENTS_SPEC = {
    "images": {"nargs": "+", "help": "Image file paths or directories", "type": str},
    "--style": {"choices": ["detailed", "brief", "technical"], "default": "detailed", "help": "Description style preference"},
    "--max-length": {"type": int, "default": 500, "metavar": "N", "help": "Maximum description length in characters"},
    "--batch-size": {"type": int, "default": 4, "metavar": "N", "help": "Number of images to process simultaneously"},
    "--timeout": {"type": int, "default": 60, "metavar": "SECONDS", "help": "Processing timeout per image"},
    "--output": {"help": "Output file path"},
    "--format": {"choices": ["plain", "json", "csv"], "default": "plain", "help": "Output format"},
    "--verbose": {"action": "store_true", "help": "Enable verbose progress output"},
    "--quiet": {"action": "store_true", "help": "Suppress all output except results"},
}

# Output Format Contracts (Enhanced but Compatible)

# Plain Format Contract (Enhanced)
PLAIN_FORMAT_TEMPLATE = """
Processed {total_images} images
Successful: {successful_count}, Failed: {failed_count}
Total time: {total_processing_time:.2f}s

{status} {image_path}
   {description}  # Now real VLM description
   Format: {format}, Size: {width}x{height}, {file_size} bytes

"""

# JSON Format Contract (Enhanced Schema)
JSON_FORMAT_SCHEMA = {
    "success": "boolean",
    "total_images": "integer",
    "successful_count": "integer",
    "failed_count": "integer",
    "total_processing_time": "number",
    "results": [
        {
            "image_path": "string",
            "description": "string",  # Real VLM description
            "confidence_score": "number|null",
            "processing_time": "number",
            "model_used": "string",  # VLM model name
            "success": "boolean",
            # New enhanced fields
            "technical_metadata": {"format": "string", "dimensions": "[width, height]", "file_size": "integer"},
            "vlm_processing_time": "number",
            "model_version": "string",
        },
    ],
}

# CSV Format Contract (Enhanced Columns)
CSV_FORMAT_COLUMNS = [
    "image_path",
    "description",  # Real VLM description
    "confidence_score",
    "processing_time",
    "success",
    # New enhanced columns
    "format",
    "width",
    "height",
    "file_size",
    "model_used",
    "model_version",
]

# Exit Code Contract (Preserved)
EXIT_CODES = {0: "Success - all images processed successfully", 1: "Error - configuration, model loading, or processing failure"}

# Environment Variable Requirements (New)
REQUIRED_ENV_VARS = {"VISION_MODEL": "VLM model identifier (e.g., 'google/gemma-3-4b')"}

OPTIONAL_ENV_VARS = {"VLM_TIMEOUT_BEHAVIOR": "Timeout behavior: 'error', 'fallback', 'continue'", "VLM_AUTO_DOWNLOAD": "Auto-download models: 'true', 'false'", "VLM_CACHE_DIR": "Model cache directory path"}

# Error Message Contract (Enhanced)
ERROR_MESSAGES = {
    "no_vision_model": "Error: VISION_MODEL environment variable not set. Please configure a VLM model.",
    "model_not_found": "Error: VLM model '{model}' not found or unavailable.",
    "model_load_failed": "Error: Failed to load VLM model '{model}': {reason}",
    "processing_timeout": "Error: VLM processing timed out after {timeout} seconds.",
    "no_images_found": "No valid image files found",  # Existing
    "processing_failed": "Error: {error_message}",  # Existing
}
