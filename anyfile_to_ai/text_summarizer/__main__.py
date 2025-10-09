"""CLI entry point for text summarizer module."""

import argparse
import json
import sys
from pathlib import Path

from .processor import summarize_text
from .exceptions import InvalidInputError, LLMError, ValidationError


def read_input(file_path: str | None, use_stdin: bool) -> str:
    """Read input text from file or stdin."""
    if use_stdin:
        return sys.stdin.read()
    if file_path:
        try:
            path = Path(file_path)
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            sys.exit(1)
        except UnicodeDecodeError:
            sys.exit(1)
    else:
        sys.exit(1)


def format_output(result, output_format: str, include_metadata: bool) -> str:
    """Format output based on requested format."""
    if output_format == "markdown":
        # Return markdown format
        from .markdown_formatter import format_markdown

        result_dict = {
            "summary": result.summary,
            "tags": result.tags,
        }
        if include_metadata and result.metadata:
            result_dict["metadata"] = {
                "input_length": result.metadata.input_length,
                "chunked": result.metadata.chunked,
                "chunk_count": result.metadata.chunk_count,
                "detected_language": result.metadata.detected_language,
                "processing_time": result.metadata.processing_time,
            }
        return format_markdown(result_dict)

    if output_format == "json":
        # Return JSON format
        data = {
            "summary": result.summary,
            "tags": result.tags,
        }
        if include_metadata and result.metadata:
            data["metadata"] = {
                "input_length": result.metadata.input_length,
                "chunked": result.metadata.chunked,
                "chunk_count": result.metadata.chunk_count,
                "detected_language": result.metadata.detected_language,
                "processing_time": result.metadata.processing_time,
            }
        return json.dumps(data, indent=2)
    if output_format == "plain":
        # Return plain text format
        lines = []
        lines.append("SUMMARY:")
        lines.append(result.summary)
        lines.append("")
        lines.append("TAGS:")
        for tag in result.tags:
            lines.append(f"- {tag}")

        if include_metadata and result.metadata:
            lines.append("")
            lines.append("METADATA:")
            lines.append(f"Input length: {result.metadata.input_length} words")
            chunked_str = "Yes" if result.metadata.chunked else "No"
            lines.append(f"Chunked: {chunked_str}")
            if result.metadata.chunk_count:
                lines.append(f"Chunk count: {result.metadata.chunk_count}")
            if result.metadata.detected_language:
                lines.append(f"Detected language: {result.metadata.detected_language}")
            lines.append(f"Processing time: {result.metadata.processing_time:.2f}s")

        return "\n".join(lines)
    msg = f"Unknown output format: {output_format}"
    raise ValueError(msg)


def write_output(content: str, output_path: str | None) -> None:
    """Write output to file or stdout."""
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    else:
        pass


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize text and generate categorization tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Input text file to summarize",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from stdin instead of file",
    )
    parser.add_argument(
        "--format",
        choices=["json", "plain", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output",
        help="Write output to file instead of stdout",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude processing metadata from output",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--model",
        default="llama3.2:latest",
        help="LLM model to use for summarization (default: llama3.2:latest)",
    )
    parser.add_argument(
        "--provider",
        default="ollama",
        choices=["ollama", "lmstudio", "mlx"],
        help="LLM provider/adapter to use (default: ollama)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.stdin and not args.file:
        parser.error("Either provide a file path or use --stdin")

    try:
        # Read input
        text = read_input(args.file, args.stdin)

        if args.verbose:
            len(text.split())

        # Summarize
        include_metadata = not args.no_metadata
        result = summarize_text(text, include_metadata=include_metadata, model=args.model, provider=args.provider)

        if args.verbose:
            pass

        # Format output
        output = format_output(result, args.format, include_metadata)

        # Write output
        write_output(output, args.output)

        sys.exit(0)

    except InvalidInputError:
        sys.exit(1)
    except LLMError:
        sys.exit(2)
    except ValidationError:
        sys.exit(3)
    except Exception:
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
