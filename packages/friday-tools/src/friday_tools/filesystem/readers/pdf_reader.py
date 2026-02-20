"""
PDF file reader adapter.

Uses pypdf for text extraction from PDF documents.
Optional dependency: pip install friday-tools[documents]

Ref: docs/build-plan/tool-improvement-build-plan.md - Phase 3a
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base import ReaderResult

logger = logging.getLogger(__name__)

# PDF extensions and MIME types
PDF_EXTENSIONS = [".pdf"]
PDF_MIMETYPES = ["application/pdf"]


class PdfReader:
    """Read text content from PDF files using pypdf.

    Handles page-based pagination, encrypted PDFs (if password provided),
    and gracefully fails when pypdf is not installed.

    Example:
        ```python
        reader = PdfReader()
        if reader.can_read(Path("document.pdf")):
            result = reader.read(Path("document.pdf"), limit=10)  # First 10 pages
            print(f"Extracted {result.page_count} pages")
        ```
    """

    @property
    def supported_extensions(self) -> list[str]:
        """PDF file extensions."""
        return PDF_EXTENSIONS

    @property
    def supported_mimetypes(self) -> list[str]:
        """PDF MIME types."""
        return PDF_MIMETYPES

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Args:
            path: Path to check

        Returns:
            True if path has a PDF extension
        """
        return path.suffix.lower() in PDF_EXTENSIONS

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read text content from a PDF file.

        Args:
            path: Path to the PDF file
            offset: Starting page number (0-indexed)
            limit: Maximum number of pages to extract (None for all)
            password: Password for encrypted PDFs
            **kwargs: Additional options (ignored)

        Returns:
            ReaderResult with extracted text and metadata
        """
        # Try to import pypdf
        try:
            from pypdf import PdfReader as PyPdfReader
            from pypdf.errors import PdfReadError
        except ImportError:
            return ReaderResult(
                content="",
                error=(
                    "PDF reading requires optional dependencies. "
                    "Install with: pip install friday-tools[documents]"
                ),
                metadata={"missing_dependency": "pypdf", "file_type": "pdf"},
            )

        try:
            # Open and read PDF
            reader = PyPdfReader(path)

            # Handle encrypted PDFs
            if reader.is_encrypted:
                if password:
                    try:
                        reader.decrypt(password)
                    except Exception as e:
                        return ReaderResult(
                            content="",
                            error=f"Failed to decrypt PDF: {e}",
                            metadata={"encrypted": True, "path": str(path)},
                        )
                else:
                    return ReaderResult(
                        content="",
                        error="PDF is encrypted. Provide password parameter to decrypt.",  # noqa: E501
                        metadata={"encrypted": True, "path": str(path)},
                    )

            total_pages = len(reader.pages)

            # Validate offset
            if offset >= total_pages:
                return ReaderResult(
                    content="",
                    error=f"Offset {offset} exceeds page count ({total_pages})",
                    page_count=total_pages,
                    metadata={"path": str(path)},
                )

            # Calculate page range
            start_page = offset
            if limit is not None:
                end_page = min(start_page + limit, total_pages)
            else:
                end_page = total_pages

            # Extract text from pages
            text_parts = []
            for page_num in range(start_page, end_page):
                page = reader.pages[page_num]
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    logger.warning(
                        f"Failed to extract text from page {page_num + 1}: {e}"
                    )
                    text_parts.append(
                        f"--- Page {page_num + 1} ---\n[Error extracting text: {e}]"
                    )

            content = "\n\n".join(text_parts)

            # Check if truncated
            truncated = end_page < total_pages

            # Gather metadata
            metadata = {
                "path": str(path),
                "title": reader.metadata.title if reader.metadata else None,
                "author": reader.metadata.author if reader.metadata else None,
                "subject": reader.metadata.subject if reader.metadata else None,
                "creator": reader.metadata.creator if reader.metadata else None,
                "producer": reader.metadata.producer if reader.metadata else None,
                "encrypted": reader.is_encrypted,
            }
            # Filter out None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            return ReaderResult(
                content=content,
                page_count=total_pages,
                truncated=truncated,
                truncated_at=end_page if truncated else None,
                metadata=metadata,
            )

        except PdfReadError as e:
            return ReaderResult(
                content="",
                error=f"Invalid or corrupted PDF: {e}",
                metadata={"path": str(path)},
            )
        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read PDF: {e}",
                metadata={"path": str(path)},
            )


# Module-level instance for convenience
pdf_reader = PdfReader()
