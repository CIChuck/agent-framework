"""
Word document reader adapter.

Uses python-docx for text extraction from DOCX files.
Optional dependency: pip install friday-tools[documents]

Ref: docs/build-plan/tool-improvement-build-plan.md - Phase 3a
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base import FileReader, ReaderResult

logger = logging.getLogger(__name__)

# DOCX extensions and MIME types
DOCX_EXTENSIONS = [".docx"]
DOCX_MIMETYPES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]


class DocxReader:
    """Read text content from Word documents using python-docx.

    Extracts paragraph text from DOCX files. Does not support older .doc format.

    Example:
        ```python
        reader = DocxReader()
        if reader.can_read(Path("document.docx")):
            result = reader.read(Path("document.docx"))
            print(result.content)
        ```
    """

    @property
    def supported_extensions(self) -> list[str]:
        """DOCX file extensions."""
        return DOCX_EXTENSIONS

    @property
    def supported_mimetypes(self) -> list[str]:
        """DOCX MIME types."""
        return DOCX_MIMETYPES

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Args:
            path: Path to check

        Returns:
            True if path has a DOCX extension
        """
        return path.suffix.lower() in DOCX_EXTENSIONS

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = None,
        include_tables: bool = True,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read text content from a Word document.

        Args:
            path: Path to the DOCX file
            offset: Starting paragraph number (0-indexed)
            limit: Maximum number of paragraphs to extract (None for all)
            include_tables: Whether to include table content
            **kwargs: Additional options (ignored)

        Returns:
            ReaderResult with extracted text and metadata
        """
        # Try to import python-docx
        try:
            from docx import Document
            from docx.opc.exceptions import PackageNotFoundError
        except ImportError:
            return ReaderResult(
                content="",
                error=(
                    "DOCX reading requires optional dependencies. "
                    "Install with: pip install friday-tools[documents]"
                ),
                metadata={"missing_dependency": "python-docx", "file_type": "docx"},
            )

        try:
            # Open document
            doc = Document(path)

            # Collect all text blocks (paragraphs and optionally tables)
            text_blocks: list[str] = []

            # Add paragraphs
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    text_blocks.append(text)

            # Add table content if requested
            if include_tables:
                for table in doc.tables:
                    table_rows = []
                    for row in table.rows:
                        row_text = " | ".join(
                            cell.text.strip() for cell in row.cells
                        )
                        if row_text.strip():
                            table_rows.append(row_text)
                    if table_rows:
                        text_blocks.append("\n".join(table_rows))

            total_blocks = len(text_blocks)

            # Validate offset
            if offset >= total_blocks and total_blocks > 0:
                return ReaderResult(
                    content="",
                    error=f"Offset {offset} exceeds paragraph count ({total_blocks})",
                    metadata={"path": str(path), "paragraph_count": total_blocks},
                )

            # Apply pagination
            start_idx = offset
            if limit is not None:
                end_idx = min(start_idx + limit, total_blocks)
            else:
                end_idx = total_blocks

            selected_blocks = text_blocks[start_idx:end_idx]
            content = "\n\n".join(selected_blocks)

            # Check if truncated
            truncated = end_idx < total_blocks

            # Gather document properties
            core_props = doc.core_properties
            metadata = {
                "path": str(path),
                "title": core_props.title,
                "author": core_props.author,
                "subject": core_props.subject,
                "keywords": core_props.keywords,
                "created": (
                    core_props.created.isoformat()
                    if core_props.created
                    else None
                ),
                "modified": (
                    core_props.modified.isoformat()
                    if core_props.modified
                    else None
                ),
                "paragraph_count": total_blocks,
                "table_count": len(doc.tables),
            }
            # Filter out None/empty values
            metadata = {k: v for k, v in metadata.items() if v}

            return ReaderResult(
                content=content,
                truncated=truncated,
                truncated_at=end_idx if truncated else None,
                metadata=metadata,
            )

        except PackageNotFoundError:
            return ReaderResult(
                content="",
                error="Invalid or corrupted DOCX file",
                metadata={"path": str(path)},
            )
        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read DOCX: {e}",
                metadata={"path": str(path)},
            )


# Module-level instance for convenience
docx_reader = DocxReader()
