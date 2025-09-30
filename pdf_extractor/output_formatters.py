"""Output formatting utilities for CLI."""

import json


class OutputFormatter:
    """Handles formatting of extraction results for different output types."""

    @staticmethod
    def print_regular_result(result, format_type: str, file_path: str):
        """Print regular extraction result."""
        if format_type == "json":
            output = {
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
                        "extraction_time": p.extraction_time
                    } for p in result.pages
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            for page in result.pages:
                print(page.text)

    @staticmethod
    def print_regular_output(pages, format_type: str, file_path: str, streaming: bool = False):
        """Print regular streaming output."""
        if format_type == "json":
            output = {
                "success": True,
                "file_path": file_path,
                "total_pages": len(pages),
                "total_chars": sum(p.char_count for p in pages),
                "pages": [
                    {
                        "page_number": p.page_number,
                        "text": p.text,
                        "char_count": p.char_count,
                        "extraction_time": p.extraction_time
                    } for p in pages
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            for page in pages:
                print(page.text)

    @staticmethod
    def print_enhanced_result(result, format_type: str, file_path: str):
        """Print enhanced extraction result with image information."""
        if format_type == "json":
            output = {
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
                        "enhanced_text": p.enhanced_text
                    } for p in result.enhanced_pages
                ]
            }
            print(json.dumps(output, indent=2))
        elif format_type == "csv":
            print("page_number,text,images_found,images_processed,processing_time")
            for page in result.enhanced_pages:
                # Escape text for CSV
                text = page.enhanced_text or page.text
                text = text.replace('"', '""').replace('\n', '\\n')
                print(f'{page.page_number},"{text}",{page.images_found},{page.images_processed},{page.extraction_time}')
        else:
            # Plain text with enhanced content
            for page in result.enhanced_pages:
                if page.enhanced_text:
                    print(page.enhanced_text)
                else:
                    print(page.text)

    @staticmethod
    def print_enhanced_output(enhanced_pages, format_type: str, file_path: str, streaming: bool = False):
        """Print enhanced streaming output."""
        if format_type == "json":
            total_images_found = sum(p.images_found for p in enhanced_pages)
            total_images_processed = sum(p.images_processed for p in enhanced_pages)
            total_images_failed = sum(p.images_failed for p in enhanced_pages)

            output = {
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
                        "enhanced_text": p.enhanced_text
                    } for p in enhanced_pages
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            for page in enhanced_pages:
                if page.enhanced_text:
                    print(page.enhanced_text)
                else:
                    print(page.text)