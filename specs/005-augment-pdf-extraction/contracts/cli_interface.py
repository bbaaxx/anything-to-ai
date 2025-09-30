"""CLI Contract: Enhanced PDF Extraction Command Line Interface

This contract defines the CLI interface for PDF extraction with optional image processing.
Contract tests must validate these CLI behaviors before implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import argparse


class EnhancedCLIInterface(ABC):
    """Interface for enhanced PDF extraction CLI."""

    @abstractmethod
    def create_parser(self) -> argparse.ArgumentParser:
        """Create CLI argument parser with image processing options.

        Returns:
            ArgumentParser with all required and optional arguments

        Required Arguments:
            file_path: Path to PDF file to process

        Optional Arguments:
            --include-images: Enable image description processing
            --image-style: Description style (brief|detailed|technical)
            --image-fallback: Custom fallback text for failed images
            --max-images: Maximum images to process per page
            --batch-size: Batch size for image processing
            --format: Output format (text|json|csv)
            --output: Output file path
            --progress: Show progress information
        """
        pass

    @abstractmethod
    def parse_args(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments.

        Args:
            args: List of command line arguments

        Returns:
            Parsed arguments namespace

        Raises:
            SystemExit: When arguments are invalid
        """
        pass

    @abstractmethod
    def validate_args(self, args: argparse.Namespace) -> None:
        """Validate parsed command line arguments.

        Args:
            args: Parsed arguments to validate

        Raises:
            ValueError: When arguments are invalid
            FileNotFoundError: When input file doesn't exist
            EnvironmentError: When image processing enabled but VISION_MODEL not set
        """
        pass

    @abstractmethod
    def execute_extraction(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute PDF extraction based on parsed arguments.

        Args:
            args: Validated command line arguments

        Returns:
            Dictionary containing extraction results and metadata

        Raises:
            PDFNotFoundError: When PDF file not found
            PDFCorruptedError: When PDF cannot be processed
            VLMConfigurationError: When vision model configuration invalid
        """
        pass

    @abstractmethod
    def format_output(
        self,
        result: Dict[str, Any],
        format_type: str
    ) -> str:
        """Format extraction results for output.

        Args:
            result: Extraction results to format
            format_type: Output format (text|json|csv)

        Returns:
            Formatted output string

        Raises:
            ValueError: When format_type is unsupported
        """
        pass


class CLIOutputFormatterInterface(ABC):
    """Interface for formatting CLI output in different formats."""

    @abstractmethod
    def format_text_output(self, result: Dict[str, Any]) -> str:
        """Format results as plain text.

        Args:
            result: Extraction results

        Returns:
            Plain text representation
        """
        pass

    @abstractmethod
    def format_json_output(self, result: Dict[str, Any]) -> str:
        """Format results as JSON.

        Args:
            result: Extraction results

        Returns:
            JSON string representation
        """
        pass

    @abstractmethod
    def format_csv_output(self, result: Dict[str, Any]) -> str:
        """Format results as CSV.

        Args:
            result: Extraction results

        Returns:
            CSV string representation
        """
        pass


class CLIProgressReporterInterface(ABC):
    """Interface for reporting CLI progress during processing."""

    @abstractmethod
    def report_start(self, file_path: str, include_images: bool) -> None:
        """Report processing start.

        Args:
            file_path: Path to file being processed
            include_images: Whether image processing is enabled
        """
        pass

    @abstractmethod
    def report_page_progress(
        self,
        page_number: int,
        total_pages: int,
        images_found: int = 0
    ) -> None:
        """Report page processing progress.

        Args:
            page_number: Current page number
            total_pages: Total number of pages
            images_found: Number of images found on page
        """
        pass

    @abstractmethod
    def report_image_progress(
        self,
        image_number: int,
        total_images: int,
        status: str
    ) -> None:
        """Report image processing progress.

        Args:
            image_number: Current image number
            total_images: Total number of images
            status: Processing status (processing|success|failed)
        """
        pass

    @abstractmethod
    def report_completion(
        self,
        total_pages: int,
        total_images: int,
        processing_time: float
    ) -> None:
        """Report processing completion.

        Args:
            total_pages: Total pages processed
            total_images: Total images processed
            processing_time: Total processing time in seconds
        """
        pass


# Contract validation functions
def validate_cli_parser(parser: argparse.ArgumentParser) -> bool:
    """Validate CLI parser contract."""
    actions = {action.dest for action in parser._actions}
    required_args = {'file_path'}
    optional_args = {
        'include_images', 'image_style', 'image_fallback',
        'max_images', 'batch_size', 'format', 'output', 'progress'
    }

    return (
        required_args.issubset(actions) and
        optional_args.issubset(actions)
    )


def validate_parsed_args(args: argparse.Namespace) -> bool:
    """Validate parsed arguments contract."""
    required_attrs = ['file_path']
    optional_attrs = [
        'include_images', 'image_style', 'image_fallback',
        'max_images', 'batch_size', 'format', 'output', 'progress'
    ]

    return (
        all(hasattr(args, attr) for attr in required_attrs) and
        all(hasattr(args, attr) for attr in optional_attrs)
    )


def validate_extraction_result_format(result: Dict[str, Any]) -> bool:
    """Validate extraction result format contract."""
    required_keys = {
        'text', 'pages', 'total_pages', 'processing_time'
    }
    optional_keys = {
        'enhanced_text', 'total_images_found', 'total_images_processed',
        'total_images_failed', 'vision_model_used', 'image_processing_time'
    }

    return (
        isinstance(result, dict) and
        required_keys.issubset(result.keys()) and
        all(key in required_keys.union(optional_keys) for key in result.keys())
    )


def validate_output_format(output: str, format_type: str) -> bool:
    """Validate output format contract."""
    if format_type == "text":
        return isinstance(output, str) and len(output) > 0
    elif format_type == "json":
        try:
            import json
            json.loads(output)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    elif format_type == "csv":
        return isinstance(output, str) and '\n' in output and ',' in output
    else:
        return False


# CLI argument specifications
CLI_ARGUMENT_SPECS = {
    'file_path': {
        'type': str,
        'help': 'Path to PDF file to process',
        'required': True
    },
    'include_images': {
        'action': 'store_true',
        'help': 'Include AI-generated descriptions of images found in PDF',
        'default': False
    },
    'image_style': {
        'choices': ['brief', 'detailed', 'technical'],
        'default': 'detailed',
        'help': 'Style of image descriptions'
    },
    'image_fallback': {
        'type': str,
        'default': '[Image: processing failed]',
        'help': 'Fallback text when image processing fails'
    },
    'max_images': {
        'type': int,
        'help': 'Maximum number of images to process per page'
    },
    'batch_size': {
        'type': int,
        'default': 4,
        'help': 'Batch size for image processing (1-10)'
    },
    'format': {
        'choices': ['text', 'json', 'csv'],
        'default': 'text',
        'help': 'Output format'
    },
    'output': {
        'type': str,
        'help': 'Output file path (default: stdout)'
    },
    'progress': {
        'action': 'store_true',
        'help': 'Show progress information',
        'default': False
    }
}


# Error message specifications
CLI_ERROR_MESSAGES = {
    'file_not_found': 'Error: PDF file not found: {file_path}',
    'invalid_format': 'Error: Unsupported output format: {format}',
    'vision_model_required': 'Error: VISION_MODEL environment variable required for image processing',
    'invalid_batch_size': 'Error: Batch size must be between 1 and 10',
    'invalid_max_images': 'Error: Maximum images per page must be positive',
    'pdf_corrupted': 'Error: PDF file is corrupted or cannot be read: {file_path}',
    'vlm_configuration': 'Error: Vision model configuration invalid: {details}',
    'processing_interrupted': 'Error: Processing was interrupted: {reason}'
}
