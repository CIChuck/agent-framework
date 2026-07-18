"""File command helpers for FridayV2."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".txt": "text",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".py": "python",
    ".csv": "csv",
    ".tsv": "tsv",
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
}


@dataclass(frozen=True)
class FileReadResult:
    """Result of reading a file for FridayV2 commands."""

    path: Path
    reader_name: str
    encoding: str
    content: str
    row_count: int | None = None
    column_count: int | None = None
    page_count: int | None = None
    sheet_names: tuple[str, ...] = ()
    truncated: bool = False


class SmartFileReader:
    """Deterministic smart-file reader for FridayV2 tests and commands."""

    def read(self, path: str | Path, *, line_limit: int | None = None) -> FileReadResult:
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {resolved}")
        if resolved.is_dir():
            raise IsADirectoryError(f"Path is a directory: {resolved}")

        extension = resolved.suffix.lower()
        reader_name = SUPPORTED_EXTENSIONS.get(extension)
        if reader_name is None:
            raise ValueError(f"Unsupported file type: {extension or '(none)'}")

        if reader_name in {"csv", "tsv"}:
            return self._read_table(resolved, reader_name, line_limit=line_limit)
        if reader_name == "json":
            return self._read_json(resolved, line_limit=line_limit)
        if reader_name in {"pdf", "docx", "xlsx"}:
            return self._read_binary_placeholder(resolved, reader_name)
        return self._read_text(resolved, reader_name, line_limit=line_limit)

    def _read_text(
        self,
        path: Path,
        reader_name: str,
        *,
        line_limit: int | None,
    ) -> FileReadResult:
        lines = path.read_text(encoding="utf-8").splitlines()
        truncated = line_limit is not None and len(lines) > line_limit
        if line_limit is not None:
            lines = lines[:line_limit]
        return FileReadResult(
            path=path,
            reader_name=reader_name,
            encoding="utf-8",
            content="\n".join(lines),
            truncated=truncated,
        )

    def _read_json(self, path: Path, *, line_limit: int | None) -> FileReadResult:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
        content = json.dumps(data, indent=2, sort_keys=True)
        lines = content.splitlines()
        truncated = line_limit is not None and len(lines) > line_limit
        if line_limit is not None:
            lines = lines[:line_limit]
        return FileReadResult(
            path=path,
            reader_name="json",
            encoding="utf-8",
            content="\n".join(lines),
            truncated=truncated,
        )

    def _read_table(
        self,
        path: Path,
        reader_name: str,
        *,
        line_limit: int | None,
    ) -> FileReadResult:
        delimiter = "\t" if reader_name == "tsv" else ","
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle, delimiter=delimiter))
        column_count = max((len(row) for row in rows), default=0)
        truncated = line_limit is not None and len(rows) > line_limit
        visible_rows = rows[:line_limit] if line_limit is not None else rows
        content = "\n".join(delimiter.join(row) for row in visible_rows)
        return FileReadResult(
            path=path,
            reader_name=reader_name,
            encoding="utf-8",
            content=content,
            row_count=len(rows),
            column_count=column_count,
            truncated=truncated,
        )

    def _read_binary_placeholder(self, path: Path, reader_name: str) -> FileReadResult:
        page_count = 1 if reader_name == "pdf" else None
        sheet_names = ("Sheet1",) if reader_name == "xlsx" else ()
        return FileReadResult(
            path=path,
            reader_name=reader_name,
            encoding="binary",
            content=f"[{reader_name} content placeholder for {path.name}]",
            page_count=page_count,
            sheet_names=sheet_names,
        )


def parse_line_limit(args: tuple[str, ...]) -> tuple[tuple[str, ...], int | None]:
    """Parse Friday-py-compatible --lines=N, defaulting malformed values to 100."""
    remaining: list[str] = []
    line_limit: int | None = None
    for arg in args:
        if not arg.startswith("--lines"):
            remaining.append(arg)
            continue
        if "=" not in arg:
            line_limit = 100
            continue
        _, value = arg.split("=", maxsplit=1)
        try:
            line_limit = int(value)
        except ValueError:
            line_limit = 100
    return tuple(remaining), line_limit


def format_file_read(result: FileReadResult) -> str:
    """Format file read output for command responses."""
    lines = [
        f"File: {result.path.name}",
        f"Reader: {result.reader_name}",
        f"Encoding: {result.encoding}",
    ]
    if result.page_count is not None:
        lines.append(f"Pages: {result.page_count}")
    if result.row_count is not None:
        lines.append(f"Rows: {result.row_count}")
    if result.column_count is not None:
        lines.append(f"Columns: {result.column_count}")
    if result.sheet_names:
        lines.append("Sheets: " + ", ".join(result.sheet_names))
    if result.truncated:
        lines.append("Truncated: true")
    lines.append("")
    lines.append(result.content)
    return "\n".join(lines)
