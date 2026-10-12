"""Dated HTTP headers, SSE framing and compatibility boundary rules."""

from __future__ import annotations

import base64
import math
import re
from dataclasses import dataclass, field
from typing import Literal

from friday_mcp.client.protocol import JSONValue, ProtocolFailure, ProtocolLimits

HTTP_COMPAT_VERSION = "2025-11-25"
type HTTPVersion = Literal["2026-07-28", "2025-11-25"]
_TOKEN = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")
_SCHEMA_MAPS = frozenset(
    {"$defs", "definitions", "patternProperties", "dependentSchemas"}
)
_SCHEMA_CHILDREN = frozenset(
    {
        "items",
        "contains",
        "additionalItems",
        "additionalProperties",
        "unevaluatedItems",
        "unevaluatedProperties",
        "propertyNames",
        "not",
        "if",
        "then",
        "else",
    }
)
_SCHEMA_ARRAYS = frozenset({"allOf", "anyOf", "oneOf", "prefixItems"})


@dataclass(frozen=True)
class HTTPLimits:
    header_bytes: int = 65536
    wire_bytes: int = 1048576
    sse_events: int = 256
    sse_line_bytes: int = 65536
    sse_event_bytes: int = 1048576

    def __post_init__(self) -> None:
        for name, ceiling in (
            ("header_bytes", 65536),
            ("wire_bytes", 1048576),
            ("sse_events", 256),
            ("sse_line_bytes", 65536),
            ("sse_event_bytes", 1048576),
        ):
            if (
                type(getattr(self, name)) is not int
                or not 0 < getattr(self, name) <= ceiling
            ):
                raise ValueError("Invalid MCP HTTP limits")


def header_value(value: str) -> bytes:
    if not isinstance(value, str):
        raise ProtocolFailure()
    try:
        raw = value.encode("utf-8")
    except UnicodeError:
        raise ProtocolFailure() from None
    if (
        value != value.strip()
        or any(not (0x20 <= ord(c) <= 0x7E or c == "\t") for c in value)
        or (value.startswith("=?base64?") and value.endswith("?="))
    ):
        return b"=?base64?" + base64.b64encode(raw) + b"?="
    return raw


@dataclass(frozen=True)
class HeaderBinding:
    name: str
    path: tuple[str, ...] = field(repr=False)
    kind: Literal["string", "boolean", "integer"]

    def extract(self, arguments: dict[str, JSONValue]) -> bytes | None:
        value: JSONValue = arguments
        for key in self.path:
            if value is None:
                return None
            if not isinstance(value, dict):
                raise ProtocolFailure()
            if key not in value:
                return None
            value = value[key]
        if value is None:
            return None
        if self.kind == "string" and isinstance(value, str):
            return header_value(value)
        if self.kind == "boolean" and type(value) is bool:
            return b"true" if value else b"false"
        if (
            self.kind == "integer"
            and type(value) in (int, float)
            and isinstance(value, (int, float))
            and abs(value) <= 2**53 - 1
            and math.isfinite(value)
            and int(value) == value
        ):
            return str(int(value)).encode("ascii")
        raise ProtocolFailure()


def header_bindings(schema: dict[str, JSONValue]) -> tuple[HeaderBinding, ...]:
    """Visit schema-bearing keywords only; example/const/default JSON is opaque."""
    bindings: list[HeaderBinding] = []
    names: set[str] = set()

    def visit(
        node: JSONValue, path: tuple[str, ...], reachable: bool, property_node: bool
    ) -> None:
        if not isinstance(node, dict):
            return
        if "x-mcp-header" in node:
            name = node["x-mcp-header"]
            kind = node.get("type")
            if (
                not reachable
                or not property_node
                or not isinstance(name, str)
                or _TOKEN.fullmatch(name) is None
                or name.lower() in names
                or kind not in ("string", "boolean", "integer")
            ):
                raise ProtocolFailure()
            if kind == "string":
                binding = HeaderBinding(name, path, "string")
            elif kind == "boolean":
                binding = HeaderBinding(name, path, "boolean")
            else:
                binding = HeaderBinding(name, path, "integer")
            names.add(name.lower())
            bindings.append(binding)
        properties = node.get("properties")
        if isinstance(properties, dict):
            for key, child in properties.items():
                visit(child, path + (key,), reachable, True)
        for key, child in node.items():
            if key in _SCHEMA_MAPS and isinstance(child, dict):
                for nested in child.values():
                    visit(nested, (), False, False)
            elif key in _SCHEMA_CHILDREN:
                if isinstance(child, list):
                    for nested in child:
                        visit(nested, (), False, False)
                else:
                    visit(child, (), False, False)
            elif key in _SCHEMA_ARRAYS and isinstance(child, list):
                for nested in child:
                    visit(nested, (), False, False)

    visit(schema, (), True, False)
    return tuple(bindings)


class SSEDecoder:
    """Incremental byte framing: no eager unbounded chunk/line/event retention."""

    def __init__(self, limits: HTTPLimits) -> None:
        self.limits = limits
        self.buffer = bytearray()
        self.data: list[str] = []
        self.event = ""
        self.event_bytes = 0
        self.wire_bytes = 0
        self.events = 0
        self.lines = 0
        self.first_line = True

    def _line(self, raw: bytes) -> bytes | None:
        self.lines += 1
        if self.lines > 4096:
            raise ProtocolFailure("limit_exceeded")
        try:
            line = raw.decode("utf-8")
        except UnicodeError:
            raise ProtocolFailure() from None
        if self.first_line:
            line = line.removeprefix("\ufeff")
            self.first_line = False
        if not line or line.startswith(":"):
            self.events += 1
            if self.events > self.limits.sse_events:
                raise ProtocolFailure("limit_exceeded")
        if not line:
            data = "\n".join(self.data).encode("utf-8") if self.data else None
            event = self.event
            self.data.clear()
            self.event = ""
            self.event_bytes = 0
            if data and event not in ("", "message"):
                raise ProtocolFailure()
            return data or None
        if line.startswith(":"):
            return None
        name, separator, value = line.partition(":")
        value = value.removeprefix(" ") if separator else ""
        if name == "data":
            self.event_bytes += len(value.encode("utf-8")) + 1
            if self.event_bytes > self.limits.sse_event_bytes:
                raise ProtocolFailure("limit_exceeded")
            self.data.append(value)
        elif name == "event":
            self.event = value
        # id/retry/unknown fields have no replay/resumption effect.
        return None

    def feed(self, chunk: bytes) -> tuple[bytes, ...]:
        self.wire_bytes += len(chunk)
        if self.wire_bytes > self.limits.wire_bytes:
            raise ProtocolFailure("limit_exceeded")
        messages: list[bytes] = []
        for byte in chunk:
            if self.buffer and self.buffer[-1] == 13:
                raw = bytes(self.buffer[:-1])
                self.buffer.clear()
                message = self._line(raw)
                if message is not None:
                    messages.append(message)
                if byte == 10:
                    continue
            if byte == 10:
                raw = bytes(self.buffer)
                self.buffer.clear()
                message = self._line(raw)
                if message is not None:
                    messages.append(message)
            else:
                self.buffer.append(byte)
                # A pending CR is a delimiter, not part of the line's byte budget.
                if len(self.buffer) - (byte == 13) > self.limits.sse_line_bytes:
                    raise ProtocolFailure("limit_exceeded")
        return tuple(messages)

    def finish(self) -> tuple[bytes, ...]:
        messages: tuple[bytes, ...] = ()
        if self.buffer and self.buffer[-1] == 13:
            raw = bytes(self.buffer[:-1])
            self.buffer.clear()
            message = self._line(raw)
            if message is not None:
                messages = (message,)
        if self.buffer or self.data:
            raise ProtocolFailure()
        return messages


def response_headers(
    headers: list[tuple[bytes, bytes]], limits: HTTPLimits
) -> dict[bytes, bytes]:
    if sum(len(k) + len(v) + 4 for k, v in headers) > limits.header_bytes:
        raise ProtocolFailure("limit_exceeded")
    result: dict[bytes, bytes] = {}
    for name, value in headers:
        key = name.lower()
        if key in result and key in (
            b"content-type",
            b"mcp-session-id",
            b"mcp-protocol-version",
        ):
            raise ProtocolFailure()
        result[key] = value
    return result


def content_type(headers: dict[bytes, bytes]) -> bytes:
    raw = headers.get(b"content-type", b"").lower().split(b";")
    if any(
        part.strip() not in (b"charset=utf-8", b'charset="utf-8"') for part in raw[1:]
    ):
        raise ProtocolFailure()
    kind = raw[0].strip()
    if kind not in (b"application/json", b"text/event-stream"):
        raise ProtocolFailure()
    return kind


def session_id(value: bytes | None) -> bytes | None:
    if value is not None and (
        not 0 < len(value) <= 256 or any(not 0x21 <= c <= 0x7E for c in value)
    ):
        raise ProtocolFailure()
    return value


def compatibility_result(
    result: dict[str, JSONValue], method: str, limits: ProtocolLimits
) -> None:
    """2025 differs from permissive 2024 defaults and modern tagged results."""
    from friday_mcp.client.protocol import validate_compatibility_fields

    validate_compatibility_fields(result, method, limits)
