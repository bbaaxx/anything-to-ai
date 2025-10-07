"""Image extraction service for PDF pages."""

import os
from typing import Any
import pdfplumber

from .enhanced_models import ImageContext
from .exceptions import PDFNotFoundError, PDFCorruptedError, ImageCroppingError


class ImageExtractor:
    """Service for extracting images from PDF pages."""

    def extract_page_images(self, page_number: int, file_path: str) -> list[ImageContext]:
        """Extract images from a specific PDF page."""
        if not os.path.exists(file_path):
            raise PDFNotFoundError(file_path)

        try:
            with pdfplumber.open(file_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    return []

                page = pdf.pages[page_number - 1]  # Convert to 0-indexed
                image_contexts = []

                for i, image_info in enumerate(page.images):
                    # Extract dimensions and validate
                    width = int(image_info.get("width", 0))
                    height = int(image_info.get("height", 0))

                    # Skip images with invalid dimensions
                    if width <= 0 or height <= 0:
                        continue

                    context = ImageContext(
                        page_number=page_number,
                        sequence_number=len(image_contexts) + 1,  # Use actual sequence
                        bounding_box=(image_info.get("x0", 0), image_info.get("y0", 0), image_info.get("x1", width), image_info.get("y1", height)),
                        width=width,
                        height=height,
                        format=image_info.get("format", "JPEG"),
                    )
                    image_contexts.append(context)

                return image_contexts

        except Exception as e:
            raise PDFCorruptedError(file_path, str(e))

    def crop_image_from_page(self, page_number: int, file_path: str, bounding_box: tuple) -> Any:
        """Crop image from PDF page using bounding box."""
        if not os.path.exists(file_path):
            raise PDFNotFoundError(file_path)

        try:
            with pdfplumber.open(file_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise ImageCroppingError(page_number, bounding_box, file_path, "Invalid page number")

                page = pdf.pages[page_number - 1]

                # Suppress warnings from pdfplumber for corrupted image metadata
                import warnings

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        # Convert PDF page to image and crop
                        page_image = page.to_image()
                        # Get the underlying PIL Image from PageImage.original
                        pil_image = page_image.original
                        cropped_image = pil_image.crop(bounding_box)
                        return cropped_image
                    except Exception as crop_error:
                        # If direct cropping fails, try alternative method
                        if "invalid float value" in str(crop_error) or "Cannot set gray" in str(crop_error):
                            raise ImageCroppingError(page_number, bounding_box, file_path, "PDF contains corrupted image metadata - image cannot be extracted")
                        raise crop_error

        except ImageCroppingError:
            # Re-raise ImageCroppingError as is
            raise
        except Exception as e:
            raise ImageCroppingError(page_number, bounding_box, file_path, str(e))
