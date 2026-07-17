# mypy: ignore-errors
"""
Reader factory for automatic file format detection.

Uses MIME type and extension-based detection to route files to appropriate readers.

Ref: docs/archive/build-plans/completed/friday-core-legacy/tool-improvement-build-plan.md - Phase 4
"""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any

from .base import ReaderResult
from .csv_reader import CsvReader
from .docx_reader import DocxReader
from .encoding import read_with_smart_encoding
from .pdf_reader import PdfReader
from .xlsx_reader import XlsxReader

logger = logging.getLogger(__name__)

# Ensure mimetypes database is initialized
mimetypes.init()


class TextReader:
    """Simple text file reader using smart encoding detection.

    This is the default fallback reader for text-based files.
    """

    COMMON_TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".rst",
        ".log",
        ".ini",
        ".cfg",
        ".conf",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".html",
        ".htm",
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".sh",
        ".bash",
        ".zsh",
        ".sql",
        ".r",
        ".m",
        ".swift",
        ".kt",
        ".scala",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".env",
        ".gitignore",
        ".dockerignore",
    }

    @property
    def supported_extensions(self) -> list[str]:
        """Common text file extensions."""
        return list(self.COMMON_TEXT_EXTENSIONS)

    @property
    def supported_mimetypes(self) -> list[str]:
        """Text MIME types."""
        return ["text/plain", "text/markdown", "text/x-python", "application/json"]

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Returns True for known text extensions or text/* MIME types.
        """
        ext = path.suffix.lower()
        if ext in self.COMMON_TEXT_EXTENSIONS:
            return True

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        return bool(mime_type and mime_type.startswith("text/"))

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read text content with smart encoding detection.

        Args:
            path: Path to the text file
            offset: Starting line number (0-indexed)
            limit: Maximum number of lines to read
            encoding: Override encoding detection

        Returns:
            ReaderResult with file content and metadata
        """
        try:
            content, enc_result = read_with_smart_encoding(
                path,
                explicit_encoding=encoding,
            )

            lines = content.splitlines(keepends=True)
            total_lines = len(lines)

            # Apply pagination
            if offset >= total_lines and total_lines > 0:
                return ReaderResult(
                    content="",
                    error=f"Offset {offset} exceeds line count ({total_lines})",
                    encoding=enc_result.encoding,
                    metadata={"path": str(path), "total_lines": total_lines},
                )

            if offset > 0:
                lines = lines[offset:]

            if limit is not None:
                truncated = len(lines) > limit
                lines = lines[:limit]
            else:
                truncated = False

            return ReaderResult(
                content="".join(lines),
                encoding=enc_result.encoding,
                truncated=truncated,
                truncated_at=offset + len(lines) if truncated else None,
                metadata={
                    "path": str(path),
                    "total_lines": total_lines,
                    "encoding_confidence": enc_result.confidence,
                    "encoding_method": enc_result.method,
                },
            )

        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read text file: {e}",
                metadata={"path": str(path)},
            )


class BinaryFallbackReader:
    """Fallback reader for binary/unknown file types.

    Extracts metadata without attempting text extraction.
    """

    def can_read(self, path: Path) -> bool:
        """Always returns True as this is the fallback."""
        return True

    @property
    def supported_extensions(self) -> list[str]:
        """No specific extensions - handles everything else."""
        return []

    @property
    def supported_mimetypes(self) -> list[str]:
        """No specific MIME types - handles everything else."""
        return []

    def read(
        self,
        path: Path,
        *,
        include_hex_preview: bool = False,
        hex_preview_bytes: int = 256,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read metadata from a binary file.

        Args:
            path: Path to the file
            include_hex_preview: Include hex dump of first bytes
            hex_preview_bytes: Number of bytes for hex preview

        Returns:
            ReaderResult with file metadata
        """
        try:
            stat_info = path.stat()

            # Detect MIME type
            mime_type, encoding = mimetypes.guess_type(str(path))

            # Read magic bytes for file type hints
            magic_bytes = b""
            try:
                with open(path, "rb") as f:
                    magic_bytes = f.read(16)
            except Exception:
                pass

            # Build content summary
            content_lines = [
                f"Binary file: {path.name}",
                f"Size: {stat_info.st_size:,} bytes",
                f"MIME type: {mime_type or 'unknown'}",
            ]

            # Add hex preview if requested
            if include_hex_preview and magic_bytes:
                with open(path, "rb") as f:
                    preview_data = f.read(hex_preview_bytes)
                hex_lines = []
                for i in range(0, len(preview_data), 16):
                    chunk = preview_data[i : i + 16]
                    hex_part = " ".join(f"{b:02x}" for b in chunk)
                    ascii_part = "".join(
                        chr(b) if 32 <= b < 127 else "." for b in chunk
                    )
                    hex_lines.append(f"{i:08x}  {hex_part:<48}  {ascii_part}")
                content_lines.append("\nHex preview:")
                content_lines.extend(hex_lines)

            metadata = {
                "path": str(path),
                "size_bytes": stat_info.st_size,
                "mime_type": mime_type,
                "mime_encoding": encoding,
                "magic_bytes": magic_bytes.hex() if magic_bytes else None,
                "is_binary": True,
            }

            return ReaderResult(
                content="\n".join(content_lines),
                metadata=metadata,
            )

        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read binary file: {e}",
                metadata={"path": str(path)},
            )


class ReaderFactory:
    """Factory for selecting appropriate file readers.

    Automatically detects file type and routes to the correct reader.
    Supports registration of custom readers.

    Example:
        ```python
        factory = ReaderFactory()

        # Read any supported file type
        result = factory.read(Path("document.pdf"))

        # Get the appropriate reader
        reader = factory.get_reader(Path("data.csv"))
        ```
    """

    def __init__(self):
        """Initialize factory with default readers."""
        # Order matters - more specific readers first
        self._readers = [
            PdfReader(),
            DocxReader(),
            XlsxReader(),
            CsvReader(),
            TextReader(),
            BinaryFallbackReader(),  # Fallback must be last
        ]

    def get_reader(self, path: Path) -> Any:
        """Get the appropriate reader for a file.

        Args:
            path: Path to the file

        Returns:
            Reader instance that can handle the file
        """
        for reader in self._readers:
            if reader.can_read(path):
                return reader

        # Should never reach here due to BinaryFallbackReader
        return self._readers[-1]

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = None,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read a file using the appropriate reader.

        Args:
            path: Path to the file to read
            offset: Starting position (line/page/row depending on format)
            limit: Maximum items to read
            **kwargs: Format-specific options

        Returns:
            ReaderResult with content and metadata
        """
        reader = self.get_reader(path)
        return reader.read(path, offset=offset, limit=limit, **kwargs)

    def register_reader(self, reader: Any, priority: int | None = None):
        """Register a custom reader.

        Args:
            reader: Reader instance implementing can_read() and read()
            priority: Position in reader list (lower = higher priority).
                     None to insert before BinaryFallbackReader.
        """
        if priority is None:
            # Insert before the fallback reader
            self._readers.insert(-1, reader)
        else:
            self._readers.insert(priority, reader)

    def get_supported_extensions(self) -> dict[str, str]:
        """Get all supported file extensions and their reader names.

        Returns:
            Dictionary mapping extensions to reader class names
        """
        extensions = {}
        for reader in self._readers:
            if hasattr(reader, "supported_extensions"):
                for ext in reader.supported_extensions:
                    if ext not in extensions:
                        extensions[ext] = reader.__class__.__name__
        return extensions


# Module-level convenience functions


def get_reader_for_path(path: Path) -> Any:
    """Get the appropriate reader for a file path.

    Args:
        path: Path to check

    Returns:
        Reader instance
    """
    factory = ReaderFactory()
    return factory.get_reader(path)
