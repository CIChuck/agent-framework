"""Extend the historical Python-open guard with SQLite path auditing."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def install() -> None:
    roots = (
        (Path.home() / ".friday").resolve(),
        (Path(os.environ["REVIEW_REPO"]) / ".friday").resolve(),
    )

    def protected(value: object) -> bool:
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        text = os.fsdecode(value)
        if text.startswith("file:"):
            text = unquote(urlsplit(text).path)
        if text in ("", ":memory:"):
            return False
        path = Path(text).expanduser().resolve()
        if sys.platform == "darwin":
            path = Path(str(path).casefold())
            compared_roots = [Path(str(root).casefold()) for root in roots]
        else:
            compared_roots = roots
        return any(path == root or path.is_relative_to(root) for root in compared_roots)

    def audit(event: str, arguments: tuple[object, ...]) -> None:
        if event == "sqlite3.connect" and protected(arguments[0]):
            raise RuntimeError("Pilot store guard blocked protected .friday path")
        # Relative os.open audit events omit dir_fd; the historical hook handles
        # ordinary relative opens. Avoid guessing their base directory here.
        if (
            event == "open"
            and isinstance(arguments[0], (str, bytes, os.PathLike))
            and Path(os.fsdecode(arguments[0])).is_absolute()
            and protected(arguments[0])
        ):
            raise RuntimeError("Pilot store guard blocked protected .friday path")

    sys.addaudithook(audit)
    original_connect = sqlite3.connect

    def connect(*args, **kwargs):
        connection = original_connect(*args, **kwargs)

        def authorize(operation, first, _second, _database, _trigger):
            if operation == sqlite3.SQLITE_ATTACH and (
                first is None or protected(first)
            ):
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        return connection

    sqlite3.connect = connect
    sqlite3.dbapi2.connect = connect
