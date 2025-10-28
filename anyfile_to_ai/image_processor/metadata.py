"""Metadata extraction for image processing."""

from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any

from PIL import Image
from PIL.ExifTags import TAGS


def extract_image_metadata(image_path: str, image_obj: Image.Image, processing_time: float, model_version: str, user_config: dict, effective_config: dict) -> dict:
    """
    Extract comprehensive metadata for image processing.

    Args:
        image_path: Path to the image file
        image_obj: PIL Image object
        processing_time: Processing duration in seconds
        model_version: VLM model version used
        user_config: User-provided configuration
        effective_config: Effective configuration after defaults

    Returns:
        Complete metadata dictionary with processing, configuration, and source sections
    """
    return {
        "processing": _extract_processing_metadata(processing_time, model_version),
        "configuration": _extract_configuration_metadata(user_config, effective_config),
        "source": _extract_image_source_metadata(image_path, image_obj),
    }


def _extract_processing_metadata(processing_time: float, model_version: str) -> dict:
    """Extract universal processing metadata."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "model_version": model_version,
        "processing_time_seconds": processing_time,
    }


def _extract_configuration_metadata(user_config: dict, effective_config: dict) -> dict:
    """Extract configuration metadata."""
    return {"user_provided": user_config, "effective": effective_config}


def _extract_image_source_metadata(image_path: str, image_obj: Image.Image) -> dict:
    """Extract image-specific source metadata including EXIF."""
    exif_data = _extract_exif_data(image_obj)
    camera_info = _extract_camera_info(exif_data)

    metadata: dict[str, Any] = {
        "file_path": image_path,
        "file_size_bytes": _get_file_size(image_path),
        "dimensions": {"width": image_obj.width, "height": image_obj.height},
        "format": image_obj.format or "unknown",
        "exif": exif_data,
    }

    if camera_info:
        metadata["camera_info"] = camera_info

    return metadata


def _get_file_size(file_path: str) -> int | str:
    """Get file size in bytes."""
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return "unavailable"


def _extract_exif_data(image_obj: Image.Image) -> dict:
    """
    Extract all available EXIF tags from image.

    Returns:
        Dictionary with human-readable EXIF tag names and values
    """
    try:
        exif_data_raw = image_obj.getexif()
        if not exif_data_raw:
            return {}

        exif_dict = {}
        for tag_id, value in exif_data_raw.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except UnicodeDecodeError:
                    continue
            exif_dict[tag_name] = value

        return exif_dict
    except (AttributeError, KeyError):
        return {}


def _extract_camera_info(exif_data: dict) -> dict:
    """Extract camera-specific information from EXIF data."""
    camera_info = {}

    if "Make" in exif_data:
        camera_info["make"] = exif_data["Make"]
    if "Model" in exif_data:
        camera_info["model"] = exif_data["Model"]
    if "LensModel" in exif_data:
        camera_info["lens"] = exif_data["LensModel"]

    return camera_info
