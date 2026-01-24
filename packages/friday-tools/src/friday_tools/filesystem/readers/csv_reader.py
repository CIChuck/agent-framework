"""
CSV file reader adapter.

Uses Python's built-in csv module with smart dialect and encoding detection.
No additional dependencies required.

Ref: docs/build-plan/tool-improvement-build-plan.md - Phase 3b
"""

from __future__ import annotations

import csv
import io
import logging
from pathlib import Path
from typing import Any, Literal

from .base import ReaderResult
from .encoding import detect_encoding

logger = logging.getLogger(__name__)

# CSV extensions and MIME types
CSV_EXTENSIONS = [".csv", ".tsv"]
CSV_MIMETYPES = ["text/csv", "text/tab-separated-values", "application/csv"]


def _format_as_markdown_table(rows: list[list[str]], headers: list[str] | None = None) -> str:
    """Format rows as a markdown table.

    Args:
        rows: List of row data
        headers: Optional header row

    Returns:
        Markdown-formatted table string
    """
    if not rows:
        return ""

    # Determine column widths
    all_rows = [headers] + rows if headers else rows
    if not all_rows:
        return ""

    num_cols = max(len(row) for row in all_rows) if all_rows else 0
    if num_cols == 0:
        return ""

    # Normalize row lengths
    normalized_rows = []
    for row in all_rows:
        normalized = list(row) + [""] * (num_cols - len(row))
        normalized_rows.append(normalized)

    # Calculate column widths
    col_widths = []
    for col_idx in range(num_cols):
        width = max(len(str(row[col_idx])) for row in normalized_rows)
        col_widths.append(max(width, 3))  # Minimum width of 3

    # Build table
    lines = []

    # Header row
    if headers:
        header_row = normalized_rows[0]
        header_line = "| " + " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(header_row)
        ) + " |"
        lines.append(header_line)

        # Separator
        sep_line = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
        lines.append(sep_line)

        data_rows = normalized_rows[1:]
    else:
        data_rows = normalized_rows

    # Data rows
    for row in data_rows:
        row_line = "| " + " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        ) + " |"
        lines.append(row_line)

    return "\n".join(lines)


class CsvReader:
    """Read CSV files with smart encoding and dialect detection.

    Automatically detects:
    - File encoding using charset-normalizer
    - CSV dialect (delimiter, quoting, etc.)

    Supports multiple output formats: raw, markdown table, or JSON-like.

    Example:
        ```python
        reader = CsvReader()
        result = reader.read(
            Path("data.csv"),
            max_rows=100,
            format_as_table=True
        )
        print(result.content)
        ```
    """

    @property
    def supported_extensions(self) -> list[str]:
        """CSV file extensions."""
        return CSV_EXTENSIONS

    @property
    def supported_mimetypes(self) -> list[str]:
        """CSV MIME types."""
        return CSV_MIMETYPES

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Args:
            path: Path to check

        Returns:
            True if path has a CSV/TSV extension
        """
        return path.suffix.lower() in CSV_EXTENSIONS

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = 1000,
        include_headers: bool = True,
        format_as_table: bool = True,
        columns: list[int] | None = None,
        delimiter: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read content from a CSV file.

        Args:
            path: Path to the CSV file
            offset: Number of data rows to skip (after header)
            limit: Maximum number of data rows to return (default: 1000)
            include_headers: Whether to include the header row
            format_as_table: Output as markdown table (True) or raw CSV (False)
            columns: List of column indices to include (0-indexed, None for all)
            delimiter: Override delimiter detection
            encoding: Override encoding detection

        Returns:
            ReaderResult with formatted content and metadata
        """
        try:
            # Detect encoding if not specified
            if encoding is None:
                enc_result = detect_encoding(path)
                encoding = enc_result.encoding
            else:
                enc_result = None

            # Read file content
            with open(path, "r", encoding=encoding, errors="replace") as f:
                content = f.read()

            # Detect dialect if delimiter not specified
            if delimiter is None:
                try:
                    # Use first 8KB for dialect detection
                    sample = content[:8192]
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    # Fall back to standard CSV
                    dialect = csv.excel
                    if path.suffix.lower() == ".tsv":
                        dialect.delimiter = "\t"
            else:
                dialect = csv.excel
                dialect.delimiter = delimiter

            # Parse CSV
            reader = csv.reader(io.StringIO(content), dialect)
            all_rows = list(reader)

            if not all_rows:
                return ReaderResult(
                    content="",
                    encoding=encoding,
                    metadata={
                        "path": str(path),
                        "row_count": 0,
                        "column_count": 0,
                    },
                )

            # Separate headers and data
            headers = all_rows[0] if include_headers else None
            data_rows = all_rows[1:] if include_headers else all_rows

            total_rows = len(data_rows)
            total_columns = max(len(row) for row in all_rows) if all_rows else 0

            # Apply column filter
            if columns is not None:
                headers = [headers[i] for i in columns if i < len(headers)] if headers else None
                data_rows = [
                    [row[i] if i < len(row) else "" for i in columns]
                    for row in data_rows
                ]

            # Apply pagination
            if offset > 0:
                data_rows = data_rows[offset:]

            if limit is not None:
                truncated = len(data_rows) > limit
                data_rows = data_rows[:limit]
            else:
                truncated = False

            # Format output
            if format_as_table:
                output = _format_as_markdown_table(data_rows, headers)
            else:
                # Raw format
                output_buffer = io.StringIO()
                writer = csv.writer(output_buffer, dialect)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data_rows)
                output = output_buffer.getvalue()

            # Build metadata
            dialect_info = {
                "delimiter": getattr(dialect, "delimiter", ","),
                "quotechar": getattr(dialect, "quotechar", '"'),
            }

            metadata = {
                "path": str(path),
                "row_count": total_rows,
                "column_count": total_columns,
                "columns": headers or [],
                "dialect": dialect_info,
                "encoding": encoding,
            }

            return ReaderResult(
                content=output,
                encoding=encoding,
                truncated=truncated,
                truncated_at=offset + len(data_rows) if truncated else None,
                metadata=metadata,
            )

        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read CSV: {e}",
                metadata={"path": str(path)},
            )


# Module-level instance for convenience
csv_reader = CsvReader()
