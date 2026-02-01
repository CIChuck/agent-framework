"""Utility helpers for Moltbook client."""

from __future__ import annotations

import os
from pathlib import Path

from .constants import (
    ALLOWED_AVATAR_EXTENSIONS,
    MAX_AVATAR_SIZE_BYTES,
    MAX_BANNER_SIZE_BYTES,
)
from .errors import MoltbookValidationError


def ensure_file_exists(path: str) -> Path:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise MoltbookValidationError(f"File not found: {path}")
    return file_path


def validate_avatar_file(path: str) -> Path:
    file_path = ensure_file_exists(path)
    suffix = file_path.suffix.lower()
    if suffix not in ALLOWED_AVATAR_EXTENSIONS:
        raise MoltbookValidationError(
            f"Avatar format '{suffix}' not allowed."
        )
    size = file_path.stat().st_size
    if size > MAX_AVATAR_SIZE_BYTES:
        raise MoltbookValidationError(
            f"Avatar file too large: {size} bytes (max {MAX_AVATAR_SIZE_BYTES})"
        )
    return file_path


def validate_banner_file(path: str) -> Path:
    file_path = ensure_file_exists(path)
    size = file_path.stat().st_size
    if size > MAX_BANNER_SIZE_BYTES:
        raise MoltbookValidationError(
            f"Banner file too large: {size} bytes (max {MAX_BANNER_SIZE_BYTES})"
        )
    return file_path


def get_env_api_key() -> str | None:
    return os.getenv("MOLTBOOK_API_KEY")
