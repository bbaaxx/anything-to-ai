# CLI Contract: Command Line Interface Specification

# Command Structure:
# python -m pdf_extractor <command> [options] <file_path>

# Available Commands:
# - extract: Extract text from PDF file
# - info: Show PDF file information

# Extract Command Contract:
# python -m pdf_extractor extract [options] <file_path>
#
# Options:
#   --stream          Enable streaming mode for large files
#   --format FORMAT   Output format: plain (default) or json
#   --progress        Show progress information during processing
#   --help           Show help message
#
# Arguments:
#   file_path        Path to PDF file to process
#
# Exit Codes:
#   0    Success
#   1    File not found or not accessible
#   2    PDF corrupted or invalid
#   3    PDF password protected
#   4    PDF contains no extractable text
#   5    Processing interrupted
#   6    Invalid arguments or options

# Info Command Contract:
# python -m pdf_extractor info <file_path>
#
# Arguments:
#   file_path        Path to PDF file to analyze
#
# Output:
#   JSON object with file information:
#   {
#     "file_path": "path/to/file.pdf",
#     "file_size": 1234567,
#     "page_count": 42,
#     "is_large_file": true,
#     "requires_streaming": true
#   }
#
# Exit Codes:
#   0    Success
#   1    File not found or not accessible
#   2    PDF corrupted or invalid
#   6    Invalid arguments

# Global Options (available for all commands):
#   --version        Show version information
#   --help          Show help message

# Output Formats:

# Plain Text Format (default):
# - One line per page
# - Pages separated by newlines
# - No metadata included

# JSON Format:
# {
#   "success": true,
#   "file_path": "path/to/file.pdf",
#   "total_pages": 42,
#   "total_chars": 12345,
#   "processing_time": 1.23,
#   "pages": [
#     {
#       "page_number": 1,
#       "text": "extracted text content",
#       "char_count": 123,
#       "extraction_time": 0.05
#     }
#   ]
# }

# Progress Output (when --progress enabled):
# Progress: [##########----------] 50% (Page 21/42) ETA: 0:30
# (Printed to stderr, not stdout)
