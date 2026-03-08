# mypy: ignore-errors
"""
Excel (XLSX) file reader adapter.

Uses openpyxl for reading Excel files.
Optional dependency: pip install friday-tools[spreadsheets]

Ref: docs/build-plan/tool-improvement-build-plan.md - Phase 3b
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base import ReaderResult

logger = logging.getLogger(__name__)

# XLSX extensions and MIME types
XLSX_EXTENSIONS = [".xlsx", ".xlsm"]
XLSX_MIMETYPES = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
]


def _format_as_markdown_table(
    rows: list[list[Any]], headers: list[str] | None = None
) -> str:
    """Format rows as a markdown table.

    Args:
        rows: List of row data
        headers: Optional header row

    Returns:
        Markdown-formatted table string
    """
    if not rows:
        return ""

    # Convert all values to strings
    str_rows = [[str(cell) if cell is not None else "" for cell in row] for row in rows]

    # Determine column widths
    all_rows = [headers] + str_rows if headers else str_rows
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
        col_widths.append(max(width, 3))

    # Build table
    lines = []

    # Header row
    if headers:
        header_row = normalized_rows[0]
        header_line = (
            "| "
            + " | ".join(
                str(cell).ljust(col_widths[i]) for i, cell in enumerate(header_row)
            )
            + " |"
        )
        lines.append(header_line)

        # Separator
        sep_line = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
        lines.append(sep_line)

        data_rows = normalized_rows[1:]
    else:
        data_rows = normalized_rows

    # Data rows
    for row in data_rows:
        row_line = (
            "| "
            + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            + " |"
        )
        lines.append(row_line)

    return "\n".join(lines)


class XlsxReader:
    """Read Excel files using openpyxl.

    Supports:
    - Sheet selection by name or index
    - Cell range specification (e.g., "A1:G100")
    - Row limiting for large files
    - Formula evaluation (returns computed values)
    - Multiple output formats

    Example:
        ```python
        reader = XlsxReader()
        result = reader.read(
            Path("report.xlsx"),
            sheet="Sales Data",
            max_rows=100
        )
        print(result.content)
        ```
    """

    @property
    def supported_extensions(self) -> list[str]:
        """Excel file extensions."""
        return XLSX_EXTENSIONS

    @property
    def supported_mimetypes(self) -> list[str]:
        """Excel MIME types."""
        return XLSX_MIMETYPES

    def can_read(self, path: Path) -> bool:
        """Check if this reader can handle the given file.

        Args:
            path: Path to check

        Returns:
            True if path has an XLSX extension
        """
        return path.suffix.lower() in XLSX_EXTENSIONS

    def read(
        self,
        path: Path,
        *,
        offset: int = 0,
        limit: int | None = 1000,
        sheet: str | int | None = None,
        cell_range: str | None = None,
        include_headers: bool = True,
        format_as_table: bool = True,
        **kwargs: Any,
    ) -> ReaderResult:
        """Read content from an Excel file.

        Args:
            path: Path to the XLSX file
            offset: Number of data rows to skip (after header)
            limit: Maximum number of data rows to return (default: 1000)
            sheet: Sheet name or index (0-indexed). None for active sheet.
            cell_range: Cell range to read (e.g., "A1:G100"). None for all.
            include_headers: Treat first row as headers
            format_as_table: Output as markdown table (True) or raw (False)

        Returns:
            ReaderResult with formatted content and metadata
        """
        # Try to import openpyxl
        try:
            from openpyxl import load_workbook
            from openpyxl.utils.exceptions import InvalidFileException
        except ImportError:
            return ReaderResult(
                content="",
                error=(
                    "Excel reading requires optional dependencies. "
                    "Install with: pip install friday-tools[spreadsheets]"
                ),
                metadata={"missing_dependency": "openpyxl", "file_type": "xlsx"},
            )

        try:
            # Open workbook in read-only mode for performance
            # data_only=True returns computed values instead of formulas
            wb = load_workbook(path, read_only=True, data_only=True)

            # Get sheet names
            sheet_names = wb.sheetnames

            # Select sheet
            if sheet is None:
                ws = wb.active
                selected_sheet = ws.title if ws else sheet_names[0]
            elif isinstance(sheet, int):
                if sheet < 0 or sheet >= len(sheet_names):
                    wb.close()
                    return ReaderResult(
                        content="",
                        error=f"Sheet index {sheet} out of range (0-{len(sheet_names) - 1})",  # noqa: E501
                        metadata={"path": str(path), "sheet_names": sheet_names},
                    )
                selected_sheet = sheet_names[sheet]
                ws = wb[selected_sheet]
            else:
                if sheet not in sheet_names:
                    wb.close()
                    return ReaderResult(
                        content="",
                        error=f"Sheet '{sheet}' not found. Available: {sheet_names}",
                        metadata={"path": str(path), "sheet_names": sheet_names},
                    )
                selected_sheet = sheet
                ws = wb[sheet]

            # Read data
            if cell_range:
                # Read specific range
                try:
                    rows = list(ws[cell_range])
                    all_rows = [[cell.value for cell in row] for row in rows]
                except Exception as e:
                    wb.close()
                    return ReaderResult(
                        content="",
                        error=f"Invalid cell range '{cell_range}': {e}",
                        metadata={"path": str(path)},
                    )
            else:
                # Read all data
                all_rows = [[cell.value for cell in row] for row in ws.iter_rows()]

            wb.close()

            if not all_rows:
                return ReaderResult(
                    content="",
                    metadata={
                        "path": str(path),
                        "sheet_name": selected_sheet,
                        "sheet_names": sheet_names,
                        "row_count": 0,
                        "column_count": 0,
                    },
                )

            # Calculate dimensions
            total_columns = max(len(row) for row in all_rows)

            # Separate headers and data
            if include_headers:
                headers = [
                    str(cell) if cell is not None else "" for cell in all_rows[0]
                ]
                data_rows = all_rows[1:]
            else:
                headers = None
                data_rows = all_rows

            total_rows = len(data_rows)

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
                # Simple text format
                lines = []
                if headers:
                    lines.append("\t".join(headers))
                for row in data_rows:
                    lines.append(
                        "\t".join(str(cell) if cell is not None else "" for cell in row)
                    )
                output = "\n".join(lines)

            # Build metadata
            metadata = {
                "path": str(path),
                "sheet_name": selected_sheet,
                "sheet_names": sheet_names,
                "row_count": total_rows,
                "column_count": total_columns,
                "columns": headers or [],
            }
            if cell_range:
                metadata["cell_range"] = cell_range

            return ReaderResult(
                content=output,
                truncated=truncated,
                truncated_at=offset + len(data_rows) if truncated else None,
                metadata=metadata,
            )

        except InvalidFileException:
            return ReaderResult(
                content="",
                error="Invalid or corrupted Excel file",
                metadata={"path": str(path)},
            )
        except Exception as e:
            return ReaderResult(
                content="",
                error=f"Failed to read Excel file: {e}",
                metadata={"path": str(path)},
            )


# Module-level instance for convenience
xlsx_reader = XlsxReader()
