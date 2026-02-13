"""Output formatting utilities for CLI."""

import os
import warnings


class OutputFormatter:
    """Handles formatting of extraction results for different output types."""

    @staticmethod
    def _warn_deprecated_internal_formatter() -> None:
        warnings.warn(
            "pdf_extractor internal formatter paths are deprecated; shared output_formatter is preferred.",
            DeprecationWarning,
            stacklevel=3,
        )

    @staticmethod
    def print_regular_result(result, format_type: str, file_path: str):
        """Print regular extraction result."""
        import sys

        if format_type in {"plain", "markdown", "json"}:
            from anyfile_to_ai.output_formatter import format_output as format_with_shared

            OutputFormatter._warn_deprecated_internal_formatter()
            payload = {
                "_json_passthrough": True,
                "content": "\n".join(page.text for page in result.pages),
                "success": result.success,
                "file_path": file_path,
                "total_pages": result.total_pages,
                "total_chars": result.total_chars,
                "processing_time": result.processing_time,
                "pages": [
                    {
                        "page_number": p.page_number,
                        "text": p.text,
                        "char_count": p.char_count,
                        "extraction_time": p.extraction_time,
                    }
                    for p in result.pages
                ],
                "filename": os.path.basename(file_path),
                "metadata": result.metadata,
            }
            print(format_with_shared("pdf", payload, format_type, include_metadata=result.metadata is not None), file=sys.stdout)
            return

        if format_type == "csv":
            import csv
            import sys

            writer = csv.writer(sys.stdout)
            headers = ["page_number", "text", "char_count", "extraction_time"]
            if result.metadata is not None:
                headers.extend(
                    [
                        "metadata.processing.timestamp",
                        "metadata.processing.model_version",
                        "metadata.processing.processing_time_seconds",
                        "metadata.source.file_path",
                        "metadata.source.file_size_bytes",
                        "metadata.source.page_count",
                    ]
                )
            writer.writerow(headers)

            for page in result.pages:
                row = [page.page_number, page.text.replace("\n", " ").replace("\r", ""), page.char_count, page.extraction_time]
                if result.metadata is not None:
                    row.extend(
                        [
                            result.metadata["processing"]["timestamp"],
                            result.metadata["processing"]["model_version"],
                            result.metadata["processing"]["processing_time_seconds"],
                            result.metadata["source"]["file_path"],
                            result.metadata["source"].get("file_size_bytes", ""),
                            result.metadata["source"].get("page_count", ""),
                        ]
                    )
                writer.writerow(row)
        else:
            for page in result.pages:
                print(page.text, file=sys.stdout)

    @staticmethod
    def print_regular_output(pages, format_type: str, file_path: str, streaming: bool = False):
        """Print regular streaming output."""
        import sys

        if format_type in {"plain", "markdown", "json"}:
            from anyfile_to_ai.output_formatter import format_output as format_with_shared

            OutputFormatter._warn_deprecated_internal_formatter()
            metadata = pages[0].metadata if pages and hasattr(pages[0], "metadata") else None
            payload = {
                "_json_passthrough": True,
                "content": "\n".join(page.text for page in pages),
                "success": True,
                "file_path": file_path,
                "total_pages": len(pages),
                "total_chars": sum(p.char_count for p in pages),
                "pages": [
                    {
                        "page_number": p.page_number,
                        "text": p.text,
                        "char_count": p.char_count,
                        "extraction_time": p.extraction_time,
                    }
                    for p in pages
                ],
                "filename": os.path.basename(file_path),
                "metadata": metadata,
            }
            print(format_with_shared("pdf", payload, format_type, include_metadata=metadata is not None), file=sys.stdout)
            return

        if format_type == "csv":
            import csv

            writer = csv.writer(sys.stdout)
            has_metadata = pages and hasattr(pages[0], "metadata") and pages[0].metadata is not None
            headers = ["page_number", "text", "char_count", "extraction_time"]
            if has_metadata:
                headers.extend(
                    [
                        "metadata.processing.timestamp",
                        "metadata.processing.model_version",
                        "metadata.source.file_path",
                    ]
                )
            writer.writerow(headers)

            for page in pages:
                row = [page.page_number, page.text.replace("\n", " ").replace("\r", ""), page.char_count, page.extraction_time]
                if has_metadata:
                    row.extend(
                        [
                            pages[0].metadata["processing"]["timestamp"],
                            pages[0].metadata["processing"]["model_version"],
                            pages[0].metadata["source"]["file_path"],
                        ]
                    )
                writer.writerow(row)
        else:
            for page in pages:
                print(page.text, file=sys.stdout)

    @staticmethod
    def print_enhanced_result(result, format_type: str, file_path: str):
        """Print enhanced extraction result with image information."""
        import json
        import sys

        if format_type == "json":
            data = {
                "success": result.success,
                "file_path": file_path,
                "total_pages": result.total_pages,
                "total_chars": result.total_chars,
                "processing_time": result.processing_time,
                "total_images_found": result.total_images_found,
                "total_images_processed": result.total_images_processed,
                "total_images_failed": result.total_images_failed,
                "image_processing_time": result.image_processing_time,
                "vision_model_used": result.vision_model_used,
                "enhanced_text": result.combined_enhanced_text,
                "pages": [
                    {
                        "page_number": p.page_number,
                        "text": p.text,
                        "char_count": p.char_count,
                        "extraction_time": p.extraction_time,
                        "images_found": p.images_found,
                        "images_processed": p.images_processed,
                        "images_failed": p.images_failed,
                        "enhanced_text": p.enhanced_text,
                    }
                    for p in result.enhanced_pages
                ],
            }
            if result.metadata is not None:
                data["metadata"] = result.metadata
            print(json.dumps(data, indent=2), file=sys.stdout)
        elif format_type == "csv":
            import csv

            writer = csv.writer(sys.stdout)
            headers = ["page_number", "text", "enhanced_text", "char_count", "images_found", "images_processed", "images_failed"]
            if result.metadata is not None:
                headers.extend(["metadata.processing.timestamp", "metadata.source.file_path"])
            writer.writerow(headers)

            for page in result.enhanced_pages:
                text = (page.enhanced_text or page.text).replace("\n", " ").replace("\r", "")
                row = [page.page_number, text, page.enhanced_text or "", page.char_count, page.images_found, page.images_processed, page.images_failed]
                if result.metadata is not None:
                    row.extend([result.metadata["processing"]["timestamp"], result.metadata["source"]["file_path"]])
                writer.writerow(row)
        else:
            for page in result.enhanced_pages:
                text = page.enhanced_text if page.enhanced_text else page.text
                print(text, file=sys.stdout)

    @staticmethod
    def print_enhanced_output(enhanced_pages, format_type: str, file_path: str, streaming: bool = False):
        """Print enhanced streaming output."""
        import json
        import sys

        if format_type == "json":
            total_images_found = sum(p.images_found for p in enhanced_pages)
            total_images_processed = sum(p.images_processed for p in enhanced_pages)
            total_images_failed = sum(p.images_failed for p in enhanced_pages)

            data = {
                "success": True,
                "file_path": file_path,
                "total_pages": len(enhanced_pages),
                "total_chars": sum(p.char_count for p in enhanced_pages),
                "total_images_found": total_images_found,
                "total_images_processed": total_images_processed,
                "total_images_failed": total_images_failed,
                "pages": [
                    {
                        "page_number": p.page_number,
                        "text": p.text,
                        "char_count": p.char_count,
                        "extraction_time": p.extraction_time,
                        "images_found": p.images_found,
                        "images_processed": p.images_processed,
                        "images_failed": p.images_failed,
                        "enhanced_text": p.enhanced_text,
                    }
                    for p in enhanced_pages
                ],
            }
            if enhanced_pages and hasattr(enhanced_pages[0], "metadata") and enhanced_pages[0].metadata is not None:
                data["metadata"] = enhanced_pages[0].metadata
            print(json.dumps(data, indent=2), file=sys.stdout)
        elif format_type == "csv":
            import csv

            writer = csv.writer(sys.stdout)
            writer.writerow(["page_number", "text", "enhanced_text", "char_count", "images_found", "images_processed", "images_failed"])
            for page in enhanced_pages:
                text = (page.enhanced_text or page.text).replace("\n", " ").replace("\r", "")
                writer.writerow([page.page_number, text, page.enhanced_text or "", page.char_count, page.images_found, page.images_processed, page.images_failed])
        else:
            for page in enhanced_pages:
                text = page.enhanced_text if page.enhanced_text else page.text
                print(text, file=sys.stdout)
