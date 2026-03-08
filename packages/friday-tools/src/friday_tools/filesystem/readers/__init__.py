# mypy: ignore-errors
"""
File format readers for the filesystem tools.

This module provides specialized readers for different file formats:
- Text files with smart encoding detection
- PDF documents (requires pypdf)
- Word documents (requires python-docx)
- CSV files (built-in)
- Excel files (requires openpyxl)

The readers use a Strategy pattern - each format has its own reader class
that implements the FileReader protocol.

Usage:
    ```python
    from friday_tools.filesystem.readers import ReaderFactory

    factory = ReaderFactory()
    result = factory.read(Path("document.pdf"))
    print(result.content)
    ```
"""

from .base import FileReader, ReaderResult
from .csv_reader import CsvReader, csv_reader
from .docx_reader import DocxReader, docx_reader
from .encoding import EncodingDetector, detect_encoding, read_with_smart_encoding
from .factory import ReaderFactory, get_reader_for_path
from .pdf_reader import PdfReader, pdf_reader
from .xlsx_reader import XlsxReader, xlsx_reader

__all__ = [
    # Base classes
    "FileReader",
    "ReaderResult",
    # Encoding utilities
    "EncodingDetector",
    "detect_encoding",
    "read_with_smart_encoding",
    # Reader classes
    "CsvReader",
    "DocxReader",
    "PdfReader",
    "XlsxReader",
    # Reader instances
    "csv_reader",
    "docx_reader",
    "pdf_reader",
    "xlsx_reader",
    # Factory
    "ReaderFactory",
    "get_reader_for_path",
]
