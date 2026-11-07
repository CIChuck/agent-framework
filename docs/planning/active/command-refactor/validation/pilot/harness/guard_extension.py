"""Extend the historical Python-open guard with SQLite path auditing."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def install() -> None:
    roots = (
        (Path.home() / ".friday").resolve(),
        (Path(os.environ["REVIEW_REPO"]) / ".friday").resolve(),
    )

    def audit(event: str, arguments: tuple[object, ...]) -> None:
        if event != "sqlite3.connect":
            return
        value = arguments[0]
        if not isinstance(value, (str, bytes, os.PathLike)):
            return
        text = os.fsdecode(value)
        if text.startswith("file:"):
            text = unquote(urlsplit(text).path)
        if text in ("", ":memory:"):
            return
        path = Path(text).expanduser().resolve()
        if any(path == root or path.is_relative_to(root) for root in roots):
            raise RuntimeError("Pilot store guard blocked protected .friday path")

    sys.addaudithook(audit)
