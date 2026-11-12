"""Strict, bounded, content-addressed control data; no third-party imports."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

RECORD_LIMIT = 1024 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


class Refusal(ValueError):
    """An explicit control/qualification refusal, also enforced under -O."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def object_value(value: object) -> dict[str, object]:
    require(isinstance(value, dict), "Expected JSON object")
    if not isinstance(value, dict):
        raise Refusal("Expected JSON object")
    result: dict[str, object] = {}
    for key, item in value.items():
        require(isinstance(key, str), "JSON key is not text")
        if isinstance(key, str):
            result[key] = item
    return result


def text(value: object) -> str:
    if not isinstance(value, str):
        raise Refusal("Expected text")
    return value


def integer(value: object, minimum: int = 0) -> int:
    require(type(value) is int, "Expected integer")
    if type(value) is not int or value < minimum:
        raise Refusal("Integer below boundary")
    return value


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise Refusal("Expected JSON array")
    return list(value)


def fields(value: object, names: set[str]) -> dict[str, object]:
    result = object_value(value)
    require(set(result) == names, "Missing or unknown control fields")
    return result


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> object:
    raise Refusal("Non-finite JSON constant: " + value)


def decode(data: bytes) -> dict[str, object]:
    require(len(data) <= RECORD_LIMIT, "Control record exceeds 1 MiB")
    try:
        value: object = json.loads(
            data, object_pairs_hook=_pairs, parse_constant=_invalid_constant
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refusal("Malformed control JSON") from exc

    # A huge exponent is legal JSON syntax but is not finite control data.
    def finite(item: object, depth: int = 0) -> None:
        require(depth <= 32, "Control nesting limit")
        if isinstance(item, float):
            require(math.isfinite(item), "Non-finite JSON number")
        elif isinstance(item, dict):
            for child in item.values():
                finite(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                finite(child, depth + 1)

    finite(value)
    return object_value(value)


def read(path: Path, expected: str | None = None) -> dict[str, object]:
    require(path.is_file() and not path.is_symlink(), "Control must be a regular file")
    with path.open("rb") as source:
        data = source.read(RECORD_LIMIT + 1)
    require(expected is None or digest(data) == expected, "Unapproved control digest")
    return decode(data)


def artifact(value: object, hosts: set[str]) -> dict[str, object]:
    result = fields(value, {"url", "sha256", "size", "license"})
    url = urlsplit(text(result["url"]))
    require(url.scheme == "https" and url.hostname in hosts, "Unapproved artifact host")
    require(
        not url.username and not url.password and not url.fragment,
        "Artifact URL has credentials/fragment",
    )
    require(bool(SHA256.fullmatch(text(result["sha256"]))), "Invalid artifact digest")
    integer(result["size"], 1)
    require(bool(text(result["license"]).strip()), "Unresolved artifact license")
    return result
