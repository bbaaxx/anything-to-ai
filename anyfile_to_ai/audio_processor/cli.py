"""
Command-line interface for audio transcription.
"""

import json
import argparse
from anyfile_to_ai.audio_processor.config import create_config
from anyfile_to_ai.audio_processor.streaming import process_audio_batch
from anyfile_to_ai.audio_processor.models import ProcessingResult
from anyfile_to_ai.audio_processor.exceptions import AudioProcessingError


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        prog="audio_processor",
        description="Process audio files with Whisper to generate text transcriptions",
    )

    # Positional arguments
    parser.add_argument("audio_files", nargs="+", help="Audio file paths (supports multiple files)")

    # Output format
    parser.add_argument(
        "--format",
        "-f",
        choices=["plain", "json", "markdown"],
        default="plain",
        help="Output format (default: plain)",
    )

    # Model selection
    parser.add_argument(
        "--model",
        "-m",
        default="medium",
        help="Whisper model selection (default: medium)",
    )

    # Quantization
    parser.add_argument(
        "--quantization",
        "-q",
        choices=["none", "4bit", "8bit"],
        default="none",
        help="Model quantization level (default: none, due to MLX compatibility)",
    )

    # Batch size
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=12,
        help="Whisper decoder batch size (default: 12)",
    )

    # Language
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default=None,
        help="Language hint (ISO 639-1 code, e.g., 'en', 'es'); auto-detects if not specified",
    )

    # Output file
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (prints to stdout if not specified)",
    )

    # Timeout
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=600,
        help="Processing timeout per file in seconds (default: 600)",
    )

    # Verbose
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose progress output")

    # Quiet
    parser.add_argument("--quiet", action="store_true", help="Suppress all output except results")

    # Timestamps
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps in transcription output (segment-level)")

    # Metadata
    parser.add_argument("--include-metadata", action="store_true", help="Include source file and processing metadata in output")

    return parser


# Alias for backward compatibility
create_parser = create_cli_parser


def format_plain_output(result: ProcessingResult, verbose: bool = False) -> str:
    """
    Format processing result as plain text.

    Args:
        result: Processing result
        verbose: Include verbose information

    Returns:
        str: Formatted plain text output
    """
    lines = []

    # Summary
    lines.append(f"Processed {result.total_files} files")
    lines.append(f"Successful: {result.successful_count}, Failed: {result.failed_count}")
    lines.append(f"Total time: {result.total_processing_time:.2f}s")
    lines.append("")

    # Individual results
    for r in result.results:
        if r.success:
            lines.append(f"✓ {r.audio_path}")
            # Use segments if available, otherwise plain text
            if r.segments:
                from anyfile_to_ai.audio_processor.markdown_formatter import format_segments_markdown

                lines.append(format_segments_markdown(r.segments))
            else:
                lines.append(f"   {r.text}")
            if verbose:
                details = f"   Duration: {r.processing_time:.1f}s, Model: {r.model_used} ({r.quantization})"
                if r.detected_language:
                    details += f", Language: {r.detected_language}"
                lines.append(details)
        else:
            lines.append(f"✗ {r.audio_path}")
            lines.append(f"   Error: {r.error_message}")
        lines.append("")

    return "\n".join(lines)


def format_markdown_output(result: ProcessingResult) -> str:
    """
    Format processing result as markdown.

    Args:
        result: Processing result

    Returns:
        str: Formatted markdown output
    """
    import os
    from anyfile_to_ai.audio_processor.markdown_formatter import format_markdown

    # Format each successful transcription as markdown
    if result.successful_count == 0:
        return "# Error\n\nNo successful transcriptions."

    # For single file, format directly
    if result.successful_count == 1:
        r = next(r for r in result.results if r.success)
        # Use actual segments if available
        if r.segments:
            from anyfile_to_ai.audio_processor.markdown_formatter import format_segments_markdown

            return format_segments_markdown(r.segments)
        result_dict = {
            "filename": os.path.basename(r.audio_path),
            "duration": r.processing_time,
            "model": r.model_used,
            "language": r.detected_language or "unknown",
            "segments": [{"start": 0.0, "end": r.processing_time, "text": r.text}],
            "metadata": getattr(r, "metadata", None),
        }
        return format_markdown(result_dict)

    # For multiple files, combine them
    lines = ["# Audio Transcriptions", ""]
    for r in result.results:
        if r.success:
            # Use actual segments if available
            if r.segments:
                from anyfile_to_ai.audio_processor.markdown_formatter import format_segments_markdown

                lines.append(f"## {os.path.basename(r.audio_path)}")
                lines.append("")
                lines.append(format_segments_markdown(r.segments))
                lines.append("")
            else:
                result_dict = {
                    "filename": os.path.basename(r.audio_path),
                    "duration": r.processing_time,
                    "model": r.model_used,
                    "language": r.detected_language or "unknown",
                    "segments": [{"start": 0.0, "end": r.processing_time, "text": r.text}],
                    "metadata": getattr(r, "metadata", None),
                }
                lines.append(format_markdown(result_dict))
                lines.append("")

    return "\n".join(lines)


def format_json_output(result: ProcessingResult) -> str:
    """
    Format processing result as JSON.

    Args:
        result: Processing result

    Returns:
        str: Formatted JSON output
    """

    # Helper function to convert result to dict
    def result_to_dict(r):
        result_dict = {
            "audio_path": r.audio_path,
            "text": r.text,
            "confidence_score": r.confidence_score,
            "processing_time": r.processing_time,
            "model_used": r.model_used,
            "quantization": r.quantization,
            "detected_language": r.detected_language,
            "success": r.success,
            "error_message": r.error_message,
        }
        # Add segments if available
        if r.segments:
            result_dict["segments"] = [{"start": seg.start, "end": seg.end, "text": seg.text} for seg in r.segments]
        # Add metadata if available
        if hasattr(r, "metadata") and r.metadata is not None:
            result_dict["metadata"] = r.metadata
        return result_dict

    output_dict = {
        "success": result.success,
        "total_files": result.total_files,
        "successful_count": result.successful_count,
        "failed_count": result.failed_count,
        "total_processing_time": result.total_processing_time,
        "average_processing_time": result.average_processing_time,
        "results": [result_to_dict(r) for r in result.results],
        "error_summary": result.error_summary,
    }

    return json.dumps(output_dict, indent=2)


def _create_progress_callback(verbose: bool, quiet: bool):
    """Create progress callback function for verbose mode."""
    if not verbose:
        return None

    def progress_cb(current, total):
        # Clear line and show progress
        if current == total:
            pass  # New line when complete

    return progress_cb


def _create_config_from_args(parsed_args, progress_callback):
    """Create configuration from parsed arguments."""
    return create_config(
        model=parsed_args.model,
        quantization=parsed_args.quantization,
        batch_size=parsed_args.batch_size,
        language=parsed_args.language,
        output_format=parsed_args.format,
        timeout_seconds=parsed_args.timeout,
        progress_callback=progress_callback,
        verbose=parsed_args.verbose,
        timestamps=parsed_args.timestamps,
    )


def _handle_output(result, parsed_args):
    """Handle output formatting and writing."""
    # Format output
    if parsed_args.format == "json":
        output = format_json_output(result)
    elif parsed_args.format == "markdown":
        output = format_markdown_output(result)
    else:
        output = format_plain_output(result, verbose=parsed_args.verbose)

    # Write output
    if parsed_args.output:
        with open(parsed_args.output, "w") as f:
            f.write(output)
        if not parsed_args.quiet:
            pass
    elif not parsed_args.quiet:
        pass


def main(args: list[str] | None = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments (uses sys.argv if not provided)

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Create progress callback for verbose mode
    progress_callback = _create_progress_callback(parsed_args.verbose, parsed_args.quiet)

    try:
        # Show initial status if verbose
        if parsed_args.verbose and not parsed_args.quiet:
            pass

        # Create configuration
        config = _create_config_from_args(parsed_args, progress_callback)

        # Process audio files
        result = process_audio_batch(parsed_args.audio_files, config, parsed_args.include_metadata)

        # Show completion message if verbose
        if parsed_args.verbose and not parsed_args.quiet:
            pass

        # Handle output
        _handle_output(result, parsed_args)

        # Return exit code based on success
        return 0 if result.successful_count > 0 else 1

    except AudioProcessingError:
        if not parsed_args.quiet:
            pass
        return 1

    except Exception:
        if not parsed_args.quiet:
            pass
        return 1
