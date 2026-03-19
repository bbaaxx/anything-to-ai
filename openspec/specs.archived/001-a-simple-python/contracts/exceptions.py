# Exception Contracts: PDF Text Extraction Module


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors"""

    def __init__(self, message: str, file_path: str | None = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.format_message())

    def format_message(self) -> str:
        if self.file_path:
            return f"{self.message}: {self.file_path}"
        return self.message


class PDFNotFoundError(PDFExtractionError):
    """Raised when PDF file does not exist or is not accessible"""

    def __init__(self, file_path: str):
        super().__init__("PDF file not found or not accessible", file_path)


class PDFCorruptedError(PDFExtractionError):
    """Raised when PDF file is corrupted or invalid"""

    def __init__(self, file_path: str, details: str | None = None):
        message = "PDF file is corrupted or invalid"
        if details:
            message += f": {details}"
        super().__init__(message, file_path)


class PDFPasswordProtectedError(PDFExtractionError):
    """Raised when PDF requires password for access"""

    def __init__(self, file_path: str):
        super().__init__("PDF file is password protected", file_path)


class PDFNoTextError(PDFExtractionError):
    """Raised when PDF contains no extractable text (images only)"""

    def __init__(self, file_path: str):
        super().__init__("PDF contains no extractable text (images only)", file_path)


class ProcessingInterruptedError(PDFExtractionError):
    """Raised when PDF processing is interrupted mid-stream"""

    def __init__(self, file_path: str, page_number: int):
        message = f"PDF processing interrupted at page {page_number}"
        super().__init__(message, file_path)
