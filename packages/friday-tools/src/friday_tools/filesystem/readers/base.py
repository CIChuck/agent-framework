"""
Base classes and protocols for file readers.

Ref: docs/build-plan/tool-improvement-build-plan.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class ReaderResult:
    """Result from a file reader operation.

    Attributes:
        content: The extracted text content
        encoding: The encoding used/detected (for text files)
        page_count: Number of pages (for documents)
        metadata: Additional format-specific metadata
        truncated: Whether content was truncated
        truncated_at: Where truncation occurred (line number, page, row, etc.)
        error: Error message if reading failed
    """

    content: str
    encoding: str | None = None
    page_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    truncated: bool = False
    truncated_at: int | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        """Whether the read operation succeeded."""
        return self.error is None


@runtime_checkable
class FileReader(Protocol):
    """Protocol for file format readers.

    Each reader implements format-specific logic for extracting text content
    from files. Readers should handle errors gracefully and return structured
    results via ReaderResult.
    """

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Args:
            path: Path to the file

        Returns:
            True if this reader supports the file format
        """
        ...

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = None,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read content from a file.

        Args:
            path: Path to the file to read
            offset: Start position (line number for text, page for documents)
            limit: Maximum items to read (lines for text, pages for documents)
            **kwargs: Format-specific options

        Returns:
            ReaderResult with extracted content and metadata
        """
        ...

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this reader supports (e.g., ['.txt', '.log'])."""
        ...

    @property
    def supported_mimetypes(self) -> list[str]:
        """List of MIME types this reader supports."""
        ...
