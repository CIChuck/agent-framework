"""Bounded, immutable MCP boundary models. No peer data in failure messages."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Literal

from jsonschema import Draft202012Validator
from referencing import Registry

type JSONValue = (
    None | bool | int | float | str | list[JSONValue] | dict[str, JSONValue]
)
type ProtocolProfile = Literal["legacy", "modern", "auto"]
type FailureCode = Literal[
    "invalid_result",
    "invalid_protocol",
    "unsupported_version",
    "limit_exceeded",
    "input_required_unsupported",
    "unsupported_content",
    "unsupported_schema",
]
LEGACY_VERSION = "2024-11-05"
MODERN_VERSION = "2026-07-28"
META_PREFIX = "io.modelcontextprotocol/"
# Only defined peer wire codes identify the modern era; local adapter codes do not.
MODERN_WIRE_ERRORS = frozenset({-32020, -32021, -32022})
_META_KEY = re.compile(
    r"(?:[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*/)?"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?)?"
)
_MESSAGES: dict[FailureCode, str] = {
    "invalid_result": "Invalid MCP tool result",
    "invalid_protocol": "Invalid MCP protocol message",
    "unsupported_version": "Unsupported MCP protocol version",
    "limit_exceeded": "MCP resource limit exceeded",
    "input_required_unsupported": "MCP input request is unsupported",
    "unsupported_content": "MCP content is unsupported",
    "unsupported_schema": "MCP output schema is unsupported",
}


class ProtocolFailure(ValueError):
    """Fixed local boundary failure, never a peer wire error."""

    def __init__(self, failure_code: FailureCode = "invalid_protocol") -> None:
        self.failure_code = failure_code
        super().__init__(_MESSAGES[failure_code])


@dataclass(frozen=True)
class ProtocolLimits:
    frame_bytes: int = 1048576
    result_bytes: int = 65536
    depth: int = 32
    concurrent_requests: int = 4
    catalog_pages: int = 16
    catalog_bytes: int = 1048576
    catalog_tools: int = 256
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        for name, ceiling in (
            ("frame_bytes", 1048576),
            ("result_bytes", 65536),
            ("depth", 32),
            ("concurrent_requests", 4),
            ("catalog_pages", 16),
            ("catalog_bytes", 1048576),
            ("catalog_tools", 256),
        ):
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= ceiling:
                raise ValueError("Invalid MCP protocol limits")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0 < self.timeout_seconds <= 30
            or not math.isfinite(self.timeout_seconds)
        ):
            raise ValueError("Invalid MCP protocol limits")


def json_value(value: object, limits: ProtocolLimits, *, byte_limit: int) -> JSONValue:
    """Validate types/depth/nodes before encoding, including non-JSON mock data."""
    nodes = 0
    characters = 0

    def visit(item: object, depth: int) -> JSONValue:
        nonlocal nodes, characters
        nodes += 1
        if depth > limits.depth or nodes > 4096:
            raise ProtocolFailure("limit_exceeded")
        if item is None or isinstance(item, bool):
            return item
        if isinstance(item, str):
            characters += len(item)
            if characters > byte_limit:
                raise ProtocolFailure("limit_exceeded")
            return item
        if isinstance(item, int):
            if item.bit_length() > 4096:
                raise ProtocolFailure("limit_exceeded")
            return item
        if isinstance(item, float) and math.isfinite(item):
            return item
        if isinstance(item, list):
            if len(item) > 4096 - nodes:
                raise ProtocolFailure("limit_exceeded")
            return [visit(child, depth + 1) for child in item]
        if isinstance(item, dict):
            if len(item) > 4096 - nodes:
                raise ProtocolFailure("limit_exceeded")
            result: dict[str, JSONValue] = {}
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ProtocolFailure()
                characters += len(key)
                if characters > byte_limit:
                    raise ProtocolFailure("limit_exceeded")
                result[key] = visit(child, depth + 1)
            return result
        raise ProtocolFailure()

    return visit(value, 0)


def encode_json(value: object, limits: ProtocolLimits, *, byte_limit: int) -> bytes:
    bounded = json_value(value, limits, byte_limit=byte_limit)
    try:
        data = json.dumps(
            bounded,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (ValueError, UnicodeError, RecursionError):
        raise ProtocolFailure() from None
    if len(data) > byte_limit:
        raise ProtocolFailure("limit_exceeded")
    return data


def _pairs(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolFailure()
        result[key] = value
    return result


def decode_json(data: bytes, limits: ProtocolLimits) -> JSONValue:
    if len(data) > limits.frame_bytes:
        raise ProtocolFailure("limit_exceeded")
    try:
        value: object = json.loads(data, object_pairs_hook=_pairs)
    except (ValueError, UnicodeError, RecursionError):
        raise ProtocolFailure() from None
    return json_value(value, limits, byte_limit=limits.frame_bytes)


@dataclass(frozen=True)
class FrozenJSON:
    """Canonical serialized JSON gives deep immutability and fresh snapshots."""

    data: bytes = field(repr=False)

    @classmethod
    def from_value(
        cls, value: object, limits: ProtocolLimits, *, byte_limit: int = 1048576
    ) -> FrozenJSON:
        return cls(encode_json(value, limits, byte_limit=byte_limit))

    def value(self) -> JSONValue:
        # Only the bounded encoder constructs internal instances.
        return decode_json(self.data, ProtocolLimits())

    def object(self) -> dict[str, JSONValue]:
        value = self.value()
        if not isinstance(value, dict):
            raise ProtocolFailure()
        return value


@dataclass(frozen=True)
class RPCResponse:
    request_id: str | int
    result: FrozenJSON | None = field(default=None, repr=False)
    error_code: int | None = None
    wire_bytes: int = 0


class ResultSnapshot(dict[str, JSONValue]):
    """Public JSON snapshot carrying exact transport accounting, never cached."""

    def __init__(self, value: dict[str, JSONValue], wire_bytes: int) -> None:
        super().__init__(value)
        self.wire_bytes = wire_bytes


def _strings(value: dict[str, JSONValue], *keys: str) -> None:
    for key in keys:
        if key in value and not isinstance(value[key], str):
            raise ProtocolFailure()


def _icons(value: dict[str, JSONValue]) -> None:
    if "icons" not in value:
        return
    icons = value["icons"]
    if not isinstance(icons, list):
        raise ProtocolFailure()
    for icon in icons:
        if not isinstance(icon, dict) or not isinstance(icon.get("src"), str):
            raise ProtocolFailure()
        _strings(icon, "mimeType")
        if "sizes" in icon and (
            not isinstance(icon["sizes"], list)
            or any(not isinstance(size, str) for size in icon["sizes"])
        ):
            raise ProtocolFailure()
        if "theme" in icon and icon["theme"] not in ("light", "dark"):
            raise ProtocolFailure()


def _implementation(value: JSONValue) -> None:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("name"), str)
        or not isinstance(value.get("version"), str)
    ):
        raise ProtocolFailure()
    _strings(value, "title", "description", "websiteUrl")
    _icons(value)


def _metadata(
    value: JSONValue, context: Literal["generic", "result", "notification"] = "generic"
) -> None:
    """Check this declared MetaObject only, never JSON values inside it."""
    if not isinstance(value, dict) or any(
        _META_KEY.fullmatch(k) is None for k in value
    ):
        raise ProtocolFailure()
    if context == "result" and META_PREFIX + "serverInfo" in value:
        _implementation(value[META_PREFIX + "serverInfo"])
    if context == "notification" and META_PREFIX + "subscriptionId" in value:
        identifier = value[META_PREFIX + "subscriptionId"]
        if isinstance(identifier, bool) or not isinstance(
            identifier, (str, int, float)
        ):
            raise ProtocolFailure()


def _server_capabilities(value: JSONValue) -> None:
    if not isinstance(value, dict) or any(
        not isinstance(v, dict) for v in value.values()
    ):
        raise ProtocolFailure()
    for key, fields in (
        ("tools", ("listChanged",)),
        ("prompts", ("listChanged",)),
        ("resources", ("listChanged", "subscribe")),
    ):
        capability = value.get(key)
        if isinstance(capability, dict):
            for name in fields:
                if name in capability and type(capability[name]) is not bool:
                    raise ProtocolFailure()
    for key in ("experimental", "extensions"):
        settings = value.get(key)
        if isinstance(settings, dict):
            if any(not isinstance(v, dict) for v in settings.values()):
                raise ProtocolFailure()
            if key == "extensions":
                _metadata(settings)
                if any("/" not in name for name in settings):
                    raise ProtocolFailure()


def _tool_optional_fields(
    tool: dict[str, JSONValue], *, modern_meta: bool = True
) -> None:
    _strings(tool, "title")
    _icons(tool)
    if "_meta" in tool:
        if modern_meta:
            _metadata(tool["_meta"])
        elif not isinstance(tool["_meta"], dict):
            raise ProtocolFailure()
    if "annotations" in tool:
        annotations = tool["annotations"]
        if not isinstance(annotations, dict):
            raise ProtocolFailure()
        _strings(annotations, "title")
        for key in (
            "readOnlyHint",
            "destructiveHint",
            "idempotentHint",
            "openWorldHint",
        ):
            if key in annotations and type(annotations[key]) is not bool:
                raise ProtocolFailure()


def _text_optional_fields(
    block: dict[str, JSONValue], *, modern_meta: bool = True
) -> None:
    if "_meta" in block:
        if modern_meta:
            _metadata(block["_meta"])
        elif not isinstance(block["_meta"], dict):
            raise ProtocolFailure()
    if "annotations" not in block:
        return
    annotations = block["annotations"]
    if not isinstance(annotations, dict):
        raise ProtocolFailure()
    _strings(annotations, "lastModified")
    if "audience" in annotations and (
        not isinstance(annotations["audience"], list)
        or any(role not in ("user", "assistant") for role in annotations["audience"])
    ):
        raise ProtocolFailure()
    if "priority" in annotations:
        priority = annotations["priority"]
        if (
            isinstance(priority, bool)
            or not isinstance(priority, (int, float))
            or not 0 <= priority <= 1
        ):
            raise ProtocolFailure()


def validate_compatibility_fields(
    result: dict[str, JSONValue],
    method: str,
    limits: ProtocolLimits,
) -> None:
    """Validate selected 2025-11-25 fields without changing 2024 stdio defaults."""
    if "_meta" in result and not isinstance(result["_meta"], dict):
        raise ProtocolFailure()
    if method == "initialize":
        _implementation(result.get("serverInfo"))
        _server_capabilities(result.get("capabilities"))
        _strings(result, "instructions", "protocolVersion")
        caps = result.get("capabilities")
        if isinstance(caps, dict) and "tasks" in caps:
            tasks = caps["tasks"]
            if not isinstance(tasks, dict):
                raise ProtocolFailure()
            for key in ("list", "cancel", "requests"):
                if key in tasks and not isinstance(tasks[key], dict):
                    raise ProtocolFailure()
            requests = tasks.get("requests")
            if isinstance(requests, dict) and "tools" in requests:
                tools = requests["tools"]
                if not isinstance(tools, dict) or (
                    "call" in tools and not isinstance(tools["call"], dict)
                ):
                    raise ProtocolFailure()
    elif method == "tools/list":
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise ProtocolFailure()
        for tool in tools:
            if not isinstance(tool, dict):
                raise ProtocolFailure()
            _tool_optional_fields(tool, modern_meta=False)
            schema = tool.get("outputSchema")
            if "outputSchema" in tool and (
                not isinstance(schema, dict) or schema.get("type") != "object"
            ):
                raise ProtocolFailure("unsupported_schema")
            execution = tool.get("execution")
            if "execution" in tool and (
                not isinstance(execution, dict)
                or (
                    "taskSupport" in execution
                    and execution["taskSupport"]
                    not in ("forbidden", "optional", "required")
                )
            ):
                raise ProtocolFailure()
    elif method == "tools/call":
        content = result.get("content")
        if (
            not isinstance(content, list)
            or type(result.get("isError", False)) is not bool
        ):
            raise ProtocolFailure("invalid_result")
        if "structuredContent" in result and not isinstance(
            result["structuredContent"], dict
        ):
            raise ProtocolFailure("invalid_result")
        for block in content:
            if not isinstance(block, dict) or not isinstance(block.get("type"), str):
                raise ProtocolFailure("invalid_result")
            if block["type"] != "text":
                raise ProtocolFailure("unsupported_content")
            if not isinstance(block.get("text"), str):
                raise ProtocolFailure("invalid_result")
            _text_optional_fields(block, modern_meta=False)


def validate_message(
    value: object, limits: ProtocolLimits, *, modern: bool = False
) -> dict[str, JSONValue]:
    bounded = json_value(value, limits, byte_limit=limits.frame_bytes)
    encode_json(bounded, limits, byte_limit=limits.frame_bytes)
    if not isinstance(bounded, dict) or bounded.get("jsonrpc") != "2.0":
        raise ProtocolFailure()
    if "_meta" in bounded and not isinstance(bounded["_meta"], dict):
        raise ProtocolFailure()
    if modern and "_meta" in bounded:
        _metadata(bounded["_meta"])
    if "id" in bounded and (
        isinstance(bounded["id"], bool) or not isinstance(bounded["id"], (str, int))
    ):
        raise ProtocolFailure()
    if "method" in bounded:
        if (
            not isinstance(bounded["method"], str)
            or not bounded["method"]
            or "result" in bounded
            or "error" in bounded
        ):
            raise ProtocolFailure()
        params = bounded.get("params", {})
        if not isinstance(params, dict) or (
            "_meta" in params and not isinstance(params["_meta"], dict)
        ):
            raise ProtocolFailure()
        if modern and "_meta" in params:
            _metadata(params["_meta"], "generic" if "id" in bounded else "notification")
    else:
        if "id" not in bounded or (("result" in bounded) == ("error" in bounded)):
            raise ProtocolFailure()
        if "result" in bounded and not isinstance(bounded["result"], dict):
            raise ProtocolFailure()
        result = bounded.get("result")
        if modern and isinstance(result, dict) and "_meta" in result:
            _metadata(result["_meta"], "result")
        if "error" in bounded:
            error = bounded["error"]
            if (
                not isinstance(error, dict)
                or type(error.get("code")) is not int
                or not isinstance(error.get("message"), str)
            ):
                raise ProtocolFailure()
    return bounded


def response_from_message(
    message: dict[str, JSONValue], limits: ProtocolLimits, wire_bytes: int = 0
) -> RPCResponse:
    request_id = message.get("id")
    if isinstance(request_id, bool) or not isinstance(request_id, (str, int)):
        raise ProtocolFailure()
    error = message.get("error")
    if isinstance(error, dict):
        code = error.get("code")
        if type(code) is not int:
            raise ProtocolFailure()
        return RPCResponse(request_id, error_code=code, wire_bytes=wire_bytes)
    return RPCResponse(
        request_id,
        result=FrozenJSON.from_value(message["result"], limits),
        wire_bytes=wire_bytes,
    )


def complete_result(result: dict[str, JSONValue], modern: bool) -> None:
    if modern and "_meta" in result:
        _metadata(result["_meta"], "result")
    kind = result.get("resultType", None if modern else "complete")
    if kind == "input_required":
        state = result.get("requestState")
        requests = result.get("inputRequests")
        if (
            (state is None and requests is None)
            or (state is not None and not isinstance(state, str))
            or (requests is not None and not isinstance(requests, dict))
        ):
            raise ProtocolFailure()
        raise ProtocolFailure("input_required_unsupported")
    if kind != "complete":
        raise ProtocolFailure("invalid_result")
    if "_meta" in result and not isinstance(result["_meta"], dict):
        raise ProtocolFailure()


@dataclass(frozen=True)
class CacheHint:
    ttl_ms: float
    scope: Literal["public", "private"]

    @classmethod
    def parse(cls, result: dict[str, JSONValue], modern: bool) -> CacheHint | None:
        if not modern and "ttlMs" not in result and "cacheScope" not in result:
            return None
        ttl = result.get("ttlMs")
        scope = result.get("cacheScope")
        if (
            isinstance(ttl, bool)
            or not isinstance(ttl, (int, float))
            or ttl < 0
            or ttl > 1e15
            or not math.isfinite(ttl)
            or scope not in ("public", "private")
        ):
            raise ProtocolFailure()
        if scope == "public":
            return cls(float(ttl), "public")
        return cls(float(ttl), "private")


@dataclass(frozen=True)
class Discovery:
    versions: tuple[str, ...] = field(repr=False)
    capabilities: FrozenJSON = field(repr=False)
    server_info: FrozenJSON = field(repr=False)
    instructions: str | None = field(repr=False)
    cache_hint: CacheHint | None = None

    @classmethod
    def parse(cls, result: dict[str, JSONValue], limits: ProtocolLimits) -> Discovery:
        result = FrozenJSON.from_value(result, limits).object()
        complete_result(result, True)
        versions = result.get("supportedVersions")
        if (
            not isinstance(versions, list)
            or not versions
            or len(versions) > 16
            or any(not isinstance(v, str) or not v for v in versions)
        ):
            raise ProtocolFailure()
        names = tuple(v for v in versions if isinstance(v, str))
        if MODERN_VERSION not in names:
            raise ProtocolFailure("unsupported_version")
        capabilities = result.get("capabilities")
        _server_capabilities(capabilities)
        meta = result.get("_meta", {})
        if not isinstance(meta, dict):
            raise ProtocolFailure()
        info = meta.get(META_PREFIX + "serverInfo", {})
        instructions = result.get("instructions")
        if "instructions" in result and not isinstance(instructions, str):
            raise ProtocolFailure()
        return cls(
            names,
            FrozenJSON.from_value(capabilities, limits),
            FrozenJSON.from_value(info, limits),
            instructions if isinstance(instructions, str) else None,
            CacheHint.parse(result, True),
        )


_SCHEMA_KEYS = frozenset(
    {
        "$schema",
        "$defs",
        "$ref",
        "type",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "prefixItems",
        "minItems",
        "maxItems",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
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


def validate_output_schema(value: object, limits: ProtocolLimits) -> FrozenJSON:
    """An acyclic, regex-free 2020-12 subset with a bounded expansion cost."""
    frozen = FrozenJSON.from_value(
        value, limits, byte_limit=min(8192, limits.frame_bytes)
    )
    root = frozen.value()
    if not isinstance(root, dict):
        raise ProtocolFailure("unsupported_schema")
    count = 0

    def visit(schema: JSONValue, ancestors: frozenset[int], depth: int) -> int:
        nonlocal count
        count += 1
        if count > 256 or depth > 16 or not isinstance(schema, (dict, bool)):
            raise ProtocolFailure("unsupported_schema")
        if isinstance(schema, bool):
            return 1
        if id(schema) in ancestors or any(
            k not in _SCHEMA_KEYS and not k.startswith("x-") for k in schema
        ):
            raise ProtocolFailure("unsupported_schema")
        ancestors = ancestors | {id(schema)}
        if (
            "$schema" in schema
            and schema["$schema"] != "https://json-schema.org/draft/2020-12/schema"
        ):
            raise ProtocolFailure("unsupported_schema")
        cost = 1
        if "$ref" in schema:
            ref = schema["$ref"]
            if not isinstance(ref, str) or not ref.startswith("#/"):
                raise ProtocolFailure("unsupported_schema")
            target: JSONValue = root
            for part in ref[2:].split("/"):
                key = part.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or key not in target:
                    raise ProtocolFailure("unsupported_schema")
                target = target[key]
            cost += visit(target, ancestors, depth + 1)
        for keyword in ("properties", "$defs"):
            children = schema.get(keyword, {})
            if not isinstance(children, dict):
                raise ProtocolFailure("unsupported_schema")
            for child in children.values():
                cost += visit(child, ancestors, depth + 1)
        for keyword in ("items", "additionalProperties"):
            if keyword in schema:
                cost += visit(schema[keyword], ancestors, depth + 1)
        children = schema.get("prefixItems", [])
        if not isinstance(children, list):
            raise ProtocolFailure("unsupported_schema")
        for child in children:
            cost += visit(child, ancestors, depth + 1)
        enum = schema.get("enum", [])
        if (
            not isinstance(enum, list)
            or len(enum) > 32
            or any(isinstance(v, (dict, list)) for v in enum)
            or isinstance(schema.get("const"), (dict, list))
        ):
            raise ProtocolFailure("unsupported_schema")
        if cost > 256:
            raise ProtocolFailure("unsupported_schema")
        return cost

    visit(root, frozenset(), 0)
    try:
        Draft202012Validator.check_schema(root)
    except Exception:
        raise ProtocolFailure("unsupported_schema") from None
    return frozen


def validate_structured(
    value: FrozenJSON | None, schema: FrozenJSON, limits: ProtocolLimits
) -> None:
    if value is None:
        raise ProtocolFailure("invalid_result")
    # Conservative upper bound for traversal/comparison work; dangerous schema
    # applicators/regular expressions/complex enum values were rejected above.
    result = value.value()

    def nodes(item: JSONValue) -> int:
        if isinstance(item, dict):
            return 1 + sum(nodes(v) for v in item.values())
        if isinstance(item, list):
            return 1 + sum(nodes(v) for v in item)
        return 1

    if nodes(result) * 256 > 65536:
        raise ProtocolFailure("limit_exceeded")
    try:
        validator = Draft202012Validator(
            schema.object(), registry=Registry[JSONValue]()
        )
        valid = validator.is_valid(result)
    except Exception:
        raise ProtocolFailure("invalid_result") from None
    if not valid:
        raise ProtocolFailure("invalid_result")


@dataclass(frozen=True)
class ToolDefinition:
    name: str = field(repr=False)
    definition: FrozenJSON = field(repr=False)
    output_schema: FrozenJSON | None = field(default=None, repr=False)

    @classmethod
    def parse(
        cls, value: object, limits: ProtocolLimits, *, modern: bool = False
    ) -> ToolDefinition:
        frozen = FrozenJSON.from_value(value, limits)
        tool = frozen.object()
        name = tool.get("name")
        schema = tool.get("inputSchema")
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(schema, dict)
            or schema.get("type") != "object"
        ):
            raise ProtocolFailure()
        if "description" in tool and not isinstance(tool["description"], str):
            raise ProtocolFailure()
        if modern:
            _tool_optional_fields(tool)
        if (
            modern
            and "$schema" in schema
            and schema["$schema"] != "https://json-schema.org/draft/2020-12/schema"
        ):
            raise ProtocolFailure("unsupported_schema")
        try:
            Draft202012Validator.check_schema(schema)
        except Exception:
            raise ProtocolFailure() from None
        output = (
            validate_output_schema(tool["outputSchema"], limits)
            if "outputSchema" in tool
            else None
        )
        return cls(name, frozen, output)


@dataclass(frozen=True)
class CatalogPage:
    tools: tuple[ToolDefinition, ...]
    cursor: str | None = field(repr=False)
    cache_hint: CacheHint | None = None

    @classmethod
    def parse(
        cls, result: dict[str, JSONValue], modern: bool, limits: ProtocolLimits
    ) -> CatalogPage:
        result = FrozenJSON.from_value(result, limits).object()
        complete_result(result, modern)
        tools = result.get("tools")
        cursor = result.get("nextCursor")
        if not isinstance(tools, list) or len(tools) > limits.catalog_tools:
            raise ProtocolFailure()
        if "nextCursor" in result and (not isinstance(cursor, str) or not cursor):
            raise ProtocolFailure()
        return cls(
            tuple(ToolDefinition.parse(t, limits, modern=modern) for t in tools),
            cursor if isinstance(cursor, str) else None,
            CacheHint.parse(result, modern),
        )


@dataclass(frozen=True)
class ToolResult:
    texts: tuple[str, ...] = field(repr=False)
    structured: FrozenJSON | None = field(repr=False)

    @classmethod
    def parse(cls, value: object, modern: bool, limits: ProtocolLimits) -> ToolResult:
        frozen = FrozenJSON.from_value(value, limits, byte_limit=limits.result_bytes)
        result = frozen.object()
        complete_result(result, modern)
        if type(result.get("isError", False)) is not bool:
            raise ProtocolFailure("invalid_result")
        # Tool failure classification is owned by the existing public adapter.
        content = result.get("content")
        if not isinstance(content, list):
            raise ProtocolFailure("invalid_result")
        texts: list[str] = []
        unsupported = False
        for block in content:
            if isinstance(block, str) and not modern:
                texts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("type"), str):
                if block["type"] == "text":
                    if modern:
                        _text_optional_fields(block)
                    text = block.get("text")
                    if not isinstance(text, str):
                        raise ProtocolFailure("invalid_result")
                    texts.append(text)
                else:
                    unsupported = True
            else:
                raise ProtocolFailure("invalid_result")
        structured = (
            FrozenJSON.from_value(
                result["structuredContent"], limits, byte_limit=limits.result_bytes
            )
            if "structuredContent" in result
            else None
        )
        if unsupported and (modern or (not any(texts) and structured is None)):
            raise ProtocolFailure("unsupported_content")
        return cls(tuple(texts), structured)

    def text(self, limits: ProtocolLimits) -> str:
        text = "\n".join(self.texts)
        if self.structured is None:
            if len(text.encode("utf-8")) > limits.result_bytes:
                raise ProtocolFailure("limit_exceeded")
            return text
        if not self.texts:
            return self.structured.data.decode("utf-8")
        return encode_json(
            {
                "content": [{"type": "text", "text": t} for t in self.texts],
                "structuredContent": self.structured.value(),
            },
            limits,
            byte_limit=limits.result_bytes,
        ).decode("utf-8")
