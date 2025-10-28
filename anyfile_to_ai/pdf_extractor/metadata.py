"""Metadata extraction for PDF processing."""

from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any


def extract_pdf_metadata(pdf_path: str, pdf_obj: Any, processing_time: float, user_config: dict, effective_config: dict) -> dict:
    """
    Extract comprehensive metadata for PDF processing.

    Args:
        pdf_path: Path to the PDF file
        pdf_obj: pdfplumber PDF object
        processing_time: Processing duration in seconds
        user_config: User-provided configuration
        effective_config: Effective configuration after defaults

    Returns:
        Complete metadata dictionary with processing, configuration, and source sections
    """
    return {
        "processing": _extract_processing_metadata(processing_time),
        "configuration": _extract_configuration_metadata(user_config, effective_config),
        "source": _extract_pdf_source_metadata(pdf_path, pdf_obj),
    }


def _extract_processing_metadata(processing_time: float) -> dict:
    """Extract universal processing metadata."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "model_version": "pdfplumber-0.11.7",
        "processing_time_seconds": processing_time,
    }


def _extract_configuration_metadata(user_config: dict, effective_config: dict) -> dict:
    """Extract configuration metadata."""
    return {"user_provided": user_config, "effective": effective_config}


def _extract_pdf_source_metadata(pdf_path: str, pdf_obj: Any) -> dict:
    """Extract PDF-specific source metadata."""
    metadata: dict[str, Any] = {
        "file_path": pdf_path,
        "file_size_bytes": _get_file_size(pdf_path),
        "page_count": len(pdf_obj.pages),
        "creation_date": _extract_pdf_creation_date(pdf_obj),
        "modification_date": _extract_pdf_modification_date(pdf_obj),
        "author": _extract_pdf_info_field(pdf_obj, "Author"),
        "title": _extract_pdf_info_field(pdf_obj, "Title"),
    }
    return metadata


def _get_file_size(file_path: str) -> int | str:
    """Get file size in bytes."""
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return "unavailable"


def _extract_pdf_creation_date(pdf_obj: Any) -> str:
    """Extract PDF creation date in ISO 8601 format."""
    try:
        if pdf_obj.metadata and "CreationDate" in pdf_obj.metadata:
            creation_date_str = pdf_obj.metadata["CreationDate"]
            return _parse_pdf_date(creation_date_str)
        return "unavailable"
    except Exception:
        return "unavailable"


def _extract_pdf_modification_date(pdf_obj: Any) -> str:
    """Extract PDF modification date in ISO 8601 format."""
    try:
        if pdf_obj.metadata and "ModDate" in pdf_obj.metadata:
            mod_date_str = pdf_obj.metadata["ModDate"]
            return _parse_pdf_date(mod_date_str)
        return "unavailable"
    except Exception:
        return "unavailable"


def _extract_pdf_info_field(pdf_obj: Any, field_name: str) -> str:
    """Extract a specific field from PDF metadata."""
    try:
        if pdf_obj.metadata and field_name in pdf_obj.metadata:
            value = pdf_obj.metadata[field_name]
            return str(value) if value else "unavailable"
        return "unavailable"
    except Exception:
        return "unavailable"


def _parse_pdf_date(pdf_date_str: str) -> str:
    """
    Parse PDF date format to ISO 8601.

    PDF date format: D:YYYYMMDDHHmmSS[+/-]HH'mm'
    Example: D:20250115093000+00'00'
    """
    try:
        if pdf_date_str.startswith("D:"):
            pdf_date_str = pdf_date_str[2:]

        year = int(pdf_date_str[0:4])
        month = int(pdf_date_str[4:6])
        day = int(pdf_date_str[6:8])
        hour = int(pdf_date_str[8:10]) if len(pdf_date_str) >= 10 else 0
        minute = int(pdf_date_str[10:12]) if len(pdf_date_str) >= 12 else 0
        second = int(pdf_date_str[12:14]) if len(pdf_date_str) >= 14 else 0

        dt = datetime(year, month, day, hour, minute, second, tzinfo=UTC)
        return dt.isoformat()
    except (ValueError, IndexError):
        return "unavailable"
