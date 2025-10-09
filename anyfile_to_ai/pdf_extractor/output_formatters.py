"""Output formatting utilities for CLI."""

from .markdown_formatter import format_extraction_result


class OutputFormatter:
    """Handles formatting of extraction results for different output types."""

    @staticmethod
    def print_regular_result(result, format_type: str, file_path: str):
        """Print regular extraction result."""
        if format_type == "json":
            {
                "success": result.success,
                "file_path": file_path,
                "total_pages": result.total_pages,
                "total_chars": result.total_chars,
                "processing_time": result.processing_time,
                "pages": [{"page_number": p.page_number, "text": p.text, "char_count": p.char_count, "extraction_time": p.extraction_time} for p in result.pages],
            }
        elif format_type == "markdown":
            import os

            filename = os.path.basename(file_path)
            format_extraction_result(result, filename)
        else:
            for _page in result.pages:
                pass

    @staticmethod
    def print_regular_output(pages, format_type: str, file_path: str, streaming: bool = False):
        """Print regular streaming output."""
        if format_type == "json":
            {
                "success": True,
                "file_path": file_path,
                "total_pages": len(pages),
                "total_chars": sum(p.char_count for p in pages),
                "pages": [{"page_number": p.page_number, "text": p.text, "char_count": p.char_count, "extraction_time": p.extraction_time} for p in pages],
            }
        elif format_type == "markdown":
            import os
            from .markdown_formatter import format_markdown

            filename = os.path.basename(file_path)
            result_dict = {"filename": filename, "pages": [{"number": p.page_number, "text": p.text} for p in pages]}
            format_markdown(result_dict)
        else:
            for _page in pages:
                pass

    @staticmethod
    def print_enhanced_result(result, format_type: str, file_path: str):
        """Print enhanced extraction result with image information."""
        if format_type == "json":
            {
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
        elif format_type == "csv":
            for page in result.enhanced_pages:
                # Escape text for CSV
                text = page.enhanced_text or page.text
                text = text.replace('"', '""').replace("\n", "\\n")
        else:
            # Plain text with enhanced content
            for page in result.enhanced_pages:
                if page.enhanced_text:
                    pass
                else:
                    pass

    @staticmethod
    def print_enhanced_output(enhanced_pages, format_type: str, file_path: str, streaming: bool = False):
        """Print enhanced streaming output."""
        if format_type == "json":
            total_images_found = sum(p.images_found for p in enhanced_pages)
            total_images_processed = sum(p.images_processed for p in enhanced_pages)
            total_images_failed = sum(p.images_failed for p in enhanced_pages)

            {
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
        else:
            for page in enhanced_pages:
                if page.enhanced_text:
                    pass
                else:
                    pass
