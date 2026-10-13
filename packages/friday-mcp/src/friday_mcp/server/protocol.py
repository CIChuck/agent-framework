"""Strict, bounded MCP2026 tools-server wire and immutable public models."""

from __future__ import annotations

import inspect
import json
import math
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal

from jsonschema import Draft202012Validator
from referencing import Registry

from friday_mcp.client.http_protocol import HeaderBinding, header_bindings
from friday_mcp.client.protocol import (
    JSONValue,
    ProtocolFailure,
    ProtocolLimits,
    ToolDefinition,
)

VERSION = "2026-07-28"
PREFIX = "io.modelcontextprotocol/"
IDENTITY: dict[str, JSONValue] = {"name": "FridayModernTools", "version": "1.0.0"}
_META_KEY = re.compile(
    r"(?:[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*/)?(?:[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?)?"
)
_SCHEMA_KEYS = frozenset(
    {
        "$schema",
        "type",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "prefixItems",
        "minItems",
        "maxItems",
        "minProperties",
        "maxProperties",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "enum",
        "const",
        "title",
        "description",
        "default",
        "examples",
        "deprecated",
        "readOnly",
        "writeOnly",
    }
)
type WireCode = Literal[-32700, -32600, -32601, -32602, -32603, -32020, -32021, -32022]
_MESSAGES: dict[WireCode, str] = {
    -32700: "Parse error",
    -32600: "Invalid request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -32020: "Header mismatch",
    -32021: "Missing required client capability",
    -32022: "Unsupported protocol version",
}


@dataclass(frozen=True)
class ServerLimits:
    """Budgets can only be lowered; deadlines never reset between phases."""

    depth: int = 32
    nodes: int = 8192
    request_bytes: int = 65536
    result_bytes: int = 65536
    catalog_bytes: int = 1048576
    catalog_tools: int = 256
    catalog_pages: int = 16
    page_tools: int = 64
    active_requests: int = 32
    header_bytes: int = 16384
    identity_bytes: int = 256
    cursor_bytes: int = 256
    timeout_seconds: float = 30.0
    shutdown_seconds: float = 0.5

    def __post_init__(self) -> None:
        ceilings = {
            "depth": 32,
            "nodes": 8192,
            "request_bytes": 65536,
            "result_bytes": 65536,
            "catalog_bytes": 1048576,
            "catalog_tools": 256,
            "catalog_pages": 16,
            "page_tools": 64,
            "active_requests": 32,
            "header_bytes": 16384,
            "identity_bytes": 256,
            "cursor_bytes": 256,
        }
        for name, ceiling in ceilings.items():
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= ceiling:
                raise ValueError("Invalid MCP server limits")
        for name, seconds_ceiling in (
            ("timeout_seconds", 30.0),
            ("shutdown_seconds", 0.5),
        ):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (float, int))
                or not math.isfinite(value)
                or not 0 < value <= seconds_ceiling
            ):
                raise ValueError("Invalid MCP server limits")


DEFAULT_SERVER_LIMITS = ServerLimits()


class ServerWireError(ValueError):
    """Only fixed normative wire errors; exception details never cross the boundary."""

    def __init__(self, code: WireCode) -> None:
        self.code = code
        super().__init__(_MESSAGES[code])

    def response(self, request_id: str | int | None = None) -> dict[str, JSONValue]:
        error: dict[str, JSONValue] = {
            "code": self.code,
            "message": _MESSAGES[self.code],
        }
        if self.code == -32022:
            error["data"] = {"supportedVersions": [VERSION]}
        result: dict[str, JSONValue] = {"jsonrpc": "2.0", "error": error}
        if request_id is not None:
            result["id"] = request_id
        return result

    @property
    def http_status(self) -> int:
        return 404 if self.code == -32601 else 500 if self.code == -32603 else 400


def bounded_json(value: object, limits: ServerLimits, byte_limit: int) -> JSONValue:
    nodes = 0
    characters = 0

    def visit(item: object, depth: int) -> JSONValue:
        nonlocal nodes, characters
        nodes += 1
        if nodes > limits.nodes or depth > limits.depth:
            raise ServerWireError(-32602)
        if item is None or isinstance(item, bool):
            return item
        if isinstance(item, str):
            try:
                item.encode("utf-8")
            except UnicodeError:
                raise ServerWireError(-32602) from None
            characters += len(item)
            if characters > byte_limit:
                raise ServerWireError(-32602)
            return item
        if isinstance(item, int):
            if item.bit_length() > 256:
                raise ServerWireError(-32602)
            return item
        if isinstance(item, float) and math.isfinite(item):
            return item
        if isinstance(item, list):
            if len(item) > limits.nodes - nodes:
                raise ServerWireError(-32602)
            return [visit(x, depth + 1) for x in item]
        if isinstance(item, dict):
            if len(item) > limits.nodes - nodes:
                raise ServerWireError(-32602)
            result: dict[str, JSONValue] = {}
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ServerWireError(-32602)
                characters += len(key)
                if characters > byte_limit:
                    raise ServerWireError(-32602)
                result[key] = visit(child, depth + 1)
            return result
        raise ServerWireError(-32602)

    return visit(value, 0)


def encode(
    value: object, limits: ServerLimits, *, byte_limit: int | None = None
) -> bytes:
    budget = limits.result_bytes if byte_limit is None else byte_limit
    clean = bounded_json(value, limits, budget)
    try:
        raw = json.dumps(
            clean,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (UnicodeError, ValueError, RecursionError):
        raise ServerWireError(-32602) from None
    if len(raw) > budget:
        raise ServerWireError(-32602)
    return raw


def _pairs(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise ServerWireError(-32700)
        result[key] = value
    return result


def decode(raw: bytes, limits: ServerLimits, *, budget: int | None = None) -> JSONValue:
    bound = limits.request_bytes if budget is None else budget
    if len(raw) > bound:
        raise ServerWireError(-32600)
    try:
        obj: object = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
        return bounded_json(obj, limits, bound)
    except ServerWireError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise ServerWireError(-32700) from None


def identifier(value: JSONValue, limits: ServerLimits) -> str | int:
    if isinstance(value, str) and len(value.encode("utf-8")) <= limits.identity_bytes:
        return value
    if type(value) is int and isinstance(value, int) and abs(value) <= 2**53 - 1:
        return value
    raise ServerWireError(-32600)


def _object(value: JSONValue) -> dict[str, JSONValue]:
    if not isinstance(value, dict):
        raise ServerWireError(-32602)
    return value


def _optional_strings(
    value: dict[str, JSONValue], keys: tuple[str, ...], limits: ServerLimits
) -> None:
    for key in keys:
        if key in value and (
            not isinstance(value[key], str)
            or len(str(value[key]).encode("utf-8")) > limits.identity_bytes
        ):
            raise ServerWireError(-32602)


def implementation(value: JSONValue, limits: ServerLimits) -> None:
    obj = _object(value)
    if not isinstance(obj.get("name"), str) or not isinstance(obj.get("version"), str):
        raise ServerWireError(-32602)
    _optional_strings(
        obj, ("name", "version", "title", "description", "websiteUrl"), limits
    )
    if "icons" in obj:
        icons = obj["icons"]
        if not isinstance(icons, list):
            raise ServerWireError(-32602)
        for icon in icons:
            i = _object(icon)
            if not isinstance(i.get("src"), str):
                raise ServerWireError(-32602)
            _optional_strings(i, ("src", "mimeType"), limits)
            if "theme" in i and i["theme"] not in ("light", "dark"):
                raise ServerWireError(-32602)
            if "sizes" in i and (
                not isinstance(i["sizes"], list)
                or any(not isinstance(x, str) for x in i["sizes"])
            ):
                raise ServerWireError(-32602)


def _trace_formats(obj: dict[str, JSONValue], limits: ServerLimits) -> None:
    """Validate reserved W3C field formats; never adopt or propagate peer context."""
    if "traceparent" in obj:
        value = obj["traceparent"]
        if not isinstance(value, str) or len(value) > limits.identity_bytes:
            raise ServerWireError(-32602)
        match = re.fullmatch(
            r"([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})(-[!-~]+)?",
            value,
        )
        if (
            match is None
            or match[1] == "ff"
            or int(match[2], 16) == 0
            or int(match[3], 16) == 0
            or match[1] == "00"
            and match[5] is not None
        ):
            raise ServerWireError(-32602)
    if "tracestate" in obj:
        state = obj["tracestate"]
        if not isinstance(state, str) or len(state) > 512:
            raise ServerWireError(-32602)
        members = state.split(",")
        if len(members) > 32:
            raise ServerWireError(-32602)
        seen: set[str] = set()
        for part in members:
            member = part.strip(" \t")
            if not member:
                continue
            key, separator, value = member.partition("=")
            if (
                not separator
                or re.fullmatch(
                    r"(?:[a-z][a-z0-9_*/-]{0,255}|[a-z0-9][a-z0-9_*/-]{0,240}@[a-z][a-z0-9_*/-]{0,13})",
                    key,
                )
                is None
                or key in seen
                or not 1 <= len(value) <= 256
                or value.endswith(" ")
                or any(not 0x20 <= ord(c) <= 0x7E or c in ",=" for c in value)
            ):
                raise ServerWireError(-32602)
            seen.add(key)
    if "baggage" in obj:
        baggage = obj["baggage"]
        if not isinstance(baggage, str) or len(baggage) > min(
            8192, limits.request_bytes
        ):
            raise ServerWireError(-32602)
        if not baggage:
            return
        members = baggage.split(",")
        if len(members) > 180:
            raise ServerWireError(-32602)
        token = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")
        for member in members:
            for index, property_text in enumerate(member.split(";")):
                key, separator, value = property_text.strip(" \t").partition("=")
                if (
                    token.fullmatch(key.rstrip(" \t")) is None
                    or index == 0
                    and not separator
                ):
                    raise ServerWireError(-32602)
                value = value.strip(" \t")
                if any(
                    not (
                        ord(c) == 0x21
                        or 0x23 <= ord(c) <= 0x2B
                        or 0x2D <= ord(c) <= 0x3A
                        or 0x3C <= ord(c) <= 0x5B
                        or 0x5D <= ord(c) <= 0x7E
                    )
                    for c in value
                ) or re.search(r"%(?![0-9A-Fa-f]{2})", value):
                    raise ServerWireError(-32602)


def metadata(
    value: JSONValue, limits: ServerLimits, *, notification: bool = False
) -> dict[str, JSONValue]:
    obj = _object(value)
    if any(_META_KEY.fullmatch(k) is None for k in obj):
        raise ServerWireError(-32602)
    _trace_formats(obj, limits)
    if notification:
        if PREFIX + "subscriptionId" in obj:
            identifier(obj[PREFIX + "subscriptionId"], limits)
        return obj
    if not isinstance(obj.get(PREFIX + "protocolVersion"), str):
        raise ServerWireError(-32602)
    caps = _object(obj.get(PREFIX + "clientCapabilities"))
    for key in ("roots", "sampling", "elicitation", "experimental", "extensions"):
        if key in caps:
            child = _object(caps[key])
            if key in ("experimental", "extensions"):
                for name, settings in child.items():
                    _object(settings)
                    if key == "extensions" and (
                        "/" not in name or _META_KEY.fullmatch(name) is None
                    ):
                        raise ServerWireError(-32602)
            if key in ("sampling", "elicitation"):
                for option in (
                    ("context", "tools") if key == "sampling" else ("form", "url")
                ):
                    if option in child:
                        _object(child[option])
    if PREFIX + "clientInfo" in obj:
        implementation(obj[PREFIX + "clientInfo"], limits)
    if "progressToken" in obj:
        progress = obj["progressToken"]
        if (
            isinstance(progress, bool)
            or not isinstance(progress, (str, int, float))
            or isinstance(progress, str)
            and len(progress.encode("utf-8")) > limits.identity_bytes
        ):
            raise ServerWireError(-32602)
    if PREFIX + "logLevel" in obj and obj[PREFIX + "logLevel"] not in (
        "debug",
        "info",
        "notice",
        "warning",
        "error",
        "critical",
        "alert",
        "emergency",
    ):
        raise ServerWireError(-32602)
    return obj


@dataclass(frozen=True)
class ServerRequest:
    request_id: str | int | None
    method: str
    params: dict[str, JSONValue] = field(repr=False)
    version: str | None = None

    @classmethod
    def parse(cls, raw: bytes, limits: ServerLimits) -> ServerRequest:
        obj = decode(raw, limits)
        if (
            not isinstance(obj, dict)
            or obj.get("jsonrpc") != "2.0"
            or any(k in obj for k in ("result", "error"))
            or not isinstance(obj.get("method"), str)
        ):
            raise ServerWireError(-32600)
        method = obj["method"]
        if (
            not isinstance(method, str)
            or not method
            or len(method.encode("utf-8")) > limits.identity_bytes
        ):
            raise ServerWireError(-32600)
        request_id = identifier(obj["id"], limits) if "id" in obj else None
        params = _object(obj.get("params", {}))
        if request_id is None:
            if "_meta" in params:
                metadata(params["_meta"], limits, notification=True)
            if method == "notifications/cancelled":
                identifier(params.get("requestId"), limits)
                if "reason" in params and not isinstance(params["reason"], str):
                    raise ServerWireError(-32602)
            return cls(None, method, params)
        meta = metadata(params.get("_meta"), limits)
        version = meta[PREFIX + "protocolVersion"]
        if not isinstance(version, str):
            raise ServerWireError(-32602)
        if "inputResponses" in params:
            raise ServerWireError(-32602)
        return cls(request_id, method, params, version)


def safe_error_id(raw: bytes, limits: ServerLimits) -> str | int | None:
    try:
        obj = decode(raw, limits)
        if (
            isinstance(obj, dict)
            and obj.get("jsonrpc") == "2.0"
            and isinstance(obj.get("method"), str)
            and not any(k in obj for k in ("result", "error"))
            and "id" in obj
        ):
            return identifier(obj["id"], limits)
    except ServerWireError:
        pass
    return None


def validate_schema(
    value: object, limits: ServerLimits, *, input_schema: bool = False
) -> bytes:
    raw = encode(value, limits, byte_limit=min(limits.catalog_bytes, 8192))
    root = decode(raw, limits, budget=8192)
    if not isinstance(root, dict) or (input_schema and root.get("type") != "object"):
        raise ValueError("Unsupported MCP tool schema")
    count = 0

    def visit(node: JSONValue, depth: int) -> None:
        nonlocal count
        count += 1
        if count > 256 or depth > 16 or not isinstance(node, (dict, bool)):
            raise ValueError("Unsupported MCP tool schema")
        if isinstance(node, bool):
            return
        if any(k not in _SCHEMA_KEYS and k != "x-mcp-header" for k in node):
            raise ValueError("Unsupported MCP tool schema")
        if (
            "$schema" in node
            and node["$schema"] != "https://json-schema.org/draft/2020-12/schema"
        ):
            raise ValueError("Unsupported MCP tool schema")
        for key in ("const", "enum"):
            val = node.get(key)
            if (
                isinstance(val, dict)
                or (key == "const" and isinstance(val, list))
                or (
                    key == "enum"
                    and (
                        not isinstance(val, list)
                        and key in node
                        or isinstance(val, list)
                        and (
                            len(val) > 32
                            or any(isinstance(v, (dict, list)) for v in val)
                        )
                    )
                )
            ):
                raise ValueError("Unsupported MCP tool schema")
        if "properties" in node:
            for child in _object(node["properties"]).values():
                visit(child, depth + 1)
        for key in ("items", "additionalProperties"):
            if key in node:
                visit(node[key], depth + 1)
        if "prefixItems" in node:
            children = node["prefixItems"]
            if not isinstance(children, list):
                raise ValueError("Unsupported MCP tool schema")
            for child in children:
                visit(child, depth + 1)

    visit(root, 0)
    try:
        Draft202012Validator.check_schema(root)
        header_bindings(root)
    except Exception:
        raise ValueError("Unsupported MCP tool schema") from None
    return raw


def schema_valid(value: JSONValue, schema: bytes, limits: ServerLimits) -> bool:
    # Bound schema x instance work so validation cannot monopolize the reader.
    def count(item: JSONValue) -> int:
        if isinstance(item, dict):
            return 1 + sum(count(v) for v in item.values())
        if isinstance(item, list):
            return 1 + sum(count(v) for v in item)
        return 1

    if count(value) * 256 > 65536:
        return False
    obj = decode(schema, limits, budget=8192)
    if not isinstance(obj, dict):
        return False
    try:
        return bool(
            Draft202012Validator(obj, registry=Registry[JSONValue]()).is_valid(value)
        )
    except Exception:
        return False


@dataclass(frozen=True)
class ToolCallResult:
    """Immutable text/structured result, preserving null versus omission."""

    _data: bytes = field(repr=False)

    @classmethod
    def text(
        cls,
        text: str,
        *,
        is_error: bool = False,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
    ) -> ToolCallResult:
        return cls.from_value(
            {"content": [{"type": "text", "text": text}], "isError": is_error},
            limits=limits,
        )

    @classmethod
    def structured(
        cls,
        value: object,
        *,
        texts: tuple[str, ...] = (),
        is_error: bool = False,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
    ) -> ToolCallResult:
        clean = bounded_json(value, limits, limits.result_bytes)
        if not texts:
            texts = (encode(clean, limits).decode("utf-8"),)
        return cls.from_value(
            {
                "content": [{"type": "text", "text": t} for t in texts],
                "structuredContent": clean,
                "isError": is_error,
            },
            limits=limits,
        )

    @classmethod
    def from_value(
        cls, value: object, *, limits: ServerLimits = DEFAULT_SERVER_LIMITS
    ) -> ToolCallResult:
        clean = bounded_json(value, limits, limits.result_bytes)
        if not isinstance(clean, dict) or any(
            k not in {"content", "structuredContent", "isError", "_meta", "resultType"}
            for k in clean
        ):
            raise ServerWireError(-32603)
        if "resultType" in clean and clean["resultType"] != "complete":
            raise ServerWireError(-32603)
        clean["resultType"] = "complete"
        if type(clean.get("isError", False)) is not bool or not isinstance(
            clean.get("content"), list
        ):
            raise ServerWireError(-32603)
        content = clean["content"]
        if not isinstance(content, list):
            raise ServerWireError(-32603)
        for block in content:
            if (
                not isinstance(block, dict)
                or block.get("type") != "text"
                or not isinstance(block.get("text"), str)
            ):
                raise ServerWireError(-32603)
            # Validate every supported dated text annotation and metadata field.
        from friday_mcp.client.protocol import ToolResult

        try:
            ToolResult.parse(
                clean,
                True,
                ProtocolLimits(result_bytes=limits.result_bytes, depth=limits.depth),
            )
        except ProtocolFailure:
            raise ServerWireError(-32603) from None
        return cls(encode(clean, limits))

    def value(
        self, limits: ServerLimits = DEFAULT_SERVER_LIMITS
    ) -> dict[str, JSONValue]:
        obj = decode(self._data, limits, budget=limits.result_bytes)
        if not isinstance(obj, dict):
            raise ServerWireError(-32603)
        return obj


type ToolHandler = Callable[[dict[str, JSONValue]], Awaitable[ToolCallResult]]


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    _definition: bytes = field(repr=False)
    _input: bytes = field(repr=False)
    _output: bytes | None = field(repr=False)
    handler: ToolHandler = field(repr=False, compare=False)
    bindings: tuple[HeaderBinding, ...] = field(repr=False)

    @classmethod
    def from_definition(
        cls,
        definition: object,
        handler: ToolHandler,
        *,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
    ) -> RegisteredTool:
        if not inspect.iscoroutinefunction(handler):
            raise ValueError("MCP handler must be async")
        clean = bounded_json(definition, limits, limits.catalog_bytes)
        if not isinstance(clean, dict):
            raise ValueError("Invalid MCP tool definition")
        try:
            parsed = ToolDefinition.parse(
                clean, ProtocolLimits(depth=limits.depth), modern=True
            )
            name = parsed.name
            if not name or len(name.encode("utf-8")) > min(128, limits.identity_bytes):
                raise ValueError("Invalid MCP tool definition")
            input_raw = validate_schema(clean["inputSchema"], limits, input_schema=True)
            output_raw = (
                validate_schema(clean["outputSchema"], limits)
                if "outputSchema" in clean
                else None
            )
            schema = decode(input_raw, limits, budget=8192)
            if not isinstance(schema, dict):
                raise ValueError("Invalid MCP tool definition")
            bindings = header_bindings(schema)
        except (ProtocolFailure, ServerWireError):
            raise ValueError("Invalid MCP tool definition") from None
        return cls(
            name,
            encode(clean, limits, byte_limit=limits.catalog_bytes),
            input_raw,
            output_raw,
            handler,
            bindings,
        )

    def definition(
        self, limits: ServerLimits = DEFAULT_SERVER_LIMITS
    ) -> dict[str, JSONValue]:
        obj = decode(self._definition, limits, budget=limits.catalog_bytes)
        if not isinstance(obj, dict):
            raise ValueError("Invalid MCP tool definition")
        return obj

    def validate_input(
        self, arguments: dict[str, JSONValue], limits: ServerLimits
    ) -> bool:
        return schema_valid(arguments, self._input, limits)

    def validate_output(
        self, result: dict[str, JSONValue], limits: ServerLimits
    ) -> bool:
        return (
            self._output is None
            or result.get("isError") is True
            or "structuredContent" in result
            and schema_valid(result["structuredContent"], self._output, limits)
        )


def notification_envelope(raw: bytes, limits: ServerLimits) -> bool:
    try:
        value = decode(raw, limits)
        return (
            isinstance(value, dict)
            and value.get("jsonrpc") == "2.0"
            and isinstance(value.get("method"), str)
            and "id" not in value
            and "result" not in value
            and "error" not in value
        )
    except ServerWireError:
        return False
