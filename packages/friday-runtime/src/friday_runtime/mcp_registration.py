"""Bounded MCP registry admission, without discovery, persistence or RPCs.

Schemas remain external content. This conservative inline subset rejects every
unknown keyword: type, properties, required, additionalProperties, items,
enum, const, default, allOf, anyOf, oneOf, not, title, description, minimum,
maximum, exclusiveMinimum, exclusiveMaximum, multipleOf, minLength, maxLength,
pattern, minItems, maxItems, uniqueItems, minProperties, maxProperties.
References, identifiers, definitions, conditionals, formats and extensions are
not implemented. Traversal is complete, at most depth 32 / 4096 JSON nodes,
and constrained by the configured complete-definition byte cap.

Costs include category/tags added by the native registry, in both plain/OpenAI
formats. A byte is conservatively budgeted as a token, not model-tokenizer parity.
Native exports remain mutable to trusted in-process callers after registration;
later prompt consumers must independently copy/verify them.
"""

from __future__ import annotations

import html
import json
import math
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Literal, Protocol

from friday_core.mcp import MCPDiagnosticCode, MCPToolMetadata, normalize_mcp_tool_name
from friday_core.security import InjectionPatternLibrary
from friday_mcp.client.adapter import MCPToolWrapper, MCPValidatedDefinition
from friday_mcp.protocols import MCPClient

from friday_runtime.config import MCPToolProviderConfig

_KEYWORDS = frozenset(
    [
        "type",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "enum",
        "const",
        "default",
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "title",
        "description",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minProperties",
        "maxProperties",
    ]
)
_TYPES = frozenset(
    ["object", "array", "string", "number", "integer", "boolean", "null"]
)
_NUMERIC = frozenset(
    ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"]
)
_COUNTS = frozenset(
    ["minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties"]
)
_PATTERNS = InjectionPatternLibrary().all_patterns
_ROLE = re.compile(
    r"<\|[^>]*(?:system|assistant|user|im_start|im_end)[^>]*\|>|\[/?(?:INST|SYSTEM|USER|ASSISTANT)\]|(?:system|assistant|user)\s*:",
    re.I,
)

MCPRegistrationReason = Literal[
    "selected", "registered", "filtered", "rejected", "capped", "unavailable", "unknown"
]


class MCPDiscoveryEntry(Protocol):
    @property
    def server_id(self) -> str: ...

    @property
    def untrusted_definition_json(self) -> str: ...


@dataclass(frozen=True)
class MCPOriginalNameSummary:
    """Bounded, lossy diagnostic only; never stores the original name.

    Length is decimal through 9999, then ``9999+``. Shape masks at most the
    first 24 characters: ASCII letters -> a, digits -> 0, -_. unchanged,
    everything else -> ?. Fingerprint is the first 12 lowercase hex digits
    of SHA-256 of the complete UTF-8 original within the handoff byte cap
    (surrogatepass for JSON-escaped lone surrogates; not export admission).
    This is neither routing provenance nor a secrecy/collision-proof hash.
    """

    length: str
    shape: str
    fingerprint: str

    def __post_init__(self) -> None:
        if (
            re.fullmatch(r"(?:0|[1-9][0-9]{0,3}|9999\+)", self.length) is None
            or re.fullmatch(r"[a0_.?\-]{0,24}", self.shape) is None
            or re.fullmatch(r"[0-9a-f]{12}", self.fingerprint) is None
        ):
            raise ValueError("Invalid MCP original-name summary")


@dataclass(frozen=True)
class MCPCollisionSource:
    """Safe configured MCP identity or explicit native registry identity."""

    provider: Literal["mcp", "native"]
    server_id: str | None = None
    original_name_summary: MCPOriginalNameSummary | None = None

    def __post_init__(self) -> None:
        if self.provider == "native":
            valid = self.server_id is None and self.original_name_summary is None
        elif self.provider == "mcp":
            valid = (
                self.server_id is not None
                and len(self.server_id) <= 64
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", self.server_id)
                is not None
                and self.original_name_summary is not None
            )
        else:
            valid = False
        if not valid:
            raise ValueError("Invalid MCP collision source")


@dataclass(frozen=True)
class MCPNameCollision:
    """First conflict only, in native-registry / discovery encounter order.

    The shared canonical name identifies the native entry without inspecting
    its internals. Sources never contain catalog/exception/configuration data.
    """

    canonical_name: str
    first: MCPCollisionSource
    second: MCPCollisionSource

    def __post_init__(self) -> None:
        if (
            len(self.canonical_name) > 64
            or re.fullmatch(r"[a-z][a-z0-9_]*", self.canonical_name) is None
        ):
            raise ValueError("Invalid MCP collision canonical name")


def _mcp_collision_source(server_id: str, original: str) -> MCPCollisionSource:
    # Called only after complete handoff size/JSON/normalization admission.
    shape = "".join(
        "a" if char.isascii() and char.isalpha() else
        "0" if char.isascii() and char.isdigit() else
        char if char in "-_." else "?"
        for char in original[:24]
    )
    return MCPCollisionSource(
        "mcp",
        server_id,
        MCPOriginalNameSummary(
            str(len(original)) if len(original) <= 9999 else "9999+",
            shape,
            sha256(original.encode("utf-8", errors="surrogatepass")).hexdigest()[:12],
        ),
    )


@dataclass(frozen=True)
class MCPRegistrationDecision:
    """Safe IDs, fixed reasons and optional bounded both-source evidence."""

    canonical_name: str | None
    server_id: str | None
    reason: MCPRegistrationReason
    code: MCPDiagnosticCode | None = None
    collision: MCPNameCollision | None = None


@dataclass(frozen=True)
class MCPBindingContext:
    decisions: tuple[MCPRegistrationDecision, ...] = ()
    prefix: str = "mcp_"
    unavailable_servers: tuple[str, ...] = ()

    def reason_for(self, name: str) -> MCPRegistrationReason | None:
        for decision in self.decisions:
            if decision.canonical_name == name:
                return decision.reason
        for server in self.unavailable_servers:
            try:
                server_prefix = normalize_mcp_tool_name(
                    server, "x", tool_name_prefix=self.prefix
                ).removesuffix("x")
            except ValueError:
                continue
            if name.startswith(server_prefix):
                return "unavailable"
        return "unknown" if self.prefix and name.startswith(self.prefix) else None


@dataclass(frozen=True)
class MCPRegistrationPlan:
    wrappers: tuple[MCPToolWrapper, ...] = field(repr=False)
    metadata: tuple[MCPToolMetadata, ...]
    decisions: tuple[MCPRegistrationDecision, ...]


class MCPRegistrationError(RuntimeError):
    """Static failure with inspectable safe decisions, not chained peer errors."""

    def __init__(
        self, code: MCPDiagnosticCode, decisions: Iterable[MCPRegistrationDecision]
    ) -> None:
        super().__init__(
            f"MCP registration failed ({code}); inspect mcp_provider.registration_decisions"
        )
        self.code = code
        self.decisions = tuple(decisions)


def _encode(value: Any) -> str:
    # Any is confined to the JSON input/export boundary.
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def exported_definition_size(tool: MCPToolWrapper) -> int:
    """Larger complete export, including native wrapper category/tag overhead."""
    return max(
        len(_encode(tool.to_schema(format)).encode("utf-8"))
        for format in ("plain", "openai")
    )


def _normalized_text(value: str) -> str:
    text = value
    for _ in range(4):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded
    else:
        raise ValueError("MCP text normalization incomplete")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = "".join(
        " " if char in "\t\r\n" else char
        for char in text
        if unicodedata.category(char) not in {"Cf", "Cc"} or char in "\t\r\n"
    )
    return " ".join(text.split())


def _unsafe(value: str) -> bool:
    normalized = _normalized_text(value)
    return bool(_ROLE.search(normalized)) or any(
        pattern.matches(value) or pattern.matches(normalized) for pattern in _PATTERNS
    )


def _semantic_text(value: str) -> None:
    if _unsafe(value) or any(
        unicodedata.category(char) in {"Cf", "Cc"} for char in value
    ):
        raise ValueError("Unsafe MCP schema semantics")


def _annotation(value: str) -> str:
    try:
        return "[redacted]" if _unsafe(value) else _normalized_text(value)
    except ValueError:
        return "[redacted]"


def _bounded_tree(
    value: Any, *, depth: int = 0, count: list[int] | None = None
) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    if depth > 32 or count[0] > 4096:
        raise ValueError("MCP schema traversal limit")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError("MCP schema keys must be strings")
            _bounded_tree(key, depth=depth + 1, count=count)
            _bounded_tree(child, depth=depth + 1, count=count)
    elif isinstance(value, list):
        for child in value:
            _bounded_tree(child, depth=depth + 1, count=count)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("MCP schema must be finite JSON")
    elif value is not None and not isinstance(value, (str, int, bool)):
        raise ValueError("MCP schema must be JSON")


def _semantic(value: Any) -> None:
    if isinstance(value, str):
        _semantic_text(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            _semantic_text(key)
            _semantic(child)
    elif isinstance(value, list):
        for child in value:
            _semantic(child)


def _schema(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if not isinstance(value, dict) or not set(value) <= _KEYWORDS:
        raise ValueError("Unsupported MCP schema")
    result: dict[str, Any] = {}
    for key, child in value.items():
        _semantic_text(key)
        if key in {"title", "description"}:
            if not isinstance(child, str):
                raise ValueError("Invalid MCP annotation")
            result[key] = _annotation(child)
        elif key == "properties":
            if not isinstance(child, dict):
                raise ValueError("Invalid MCP properties")
            result[key] = {}
            for name, sub in child.items():
                _semantic_text(name)
                result[key][name] = _schema(sub)
        elif key in {"items", "additionalProperties", "not"}:
            result[key] = _schema(child)
        elif key in {"allOf", "anyOf", "oneOf"}:
            if not isinstance(child, list) or not child:
                raise ValueError("Invalid MCP combinator")
            result[key] = [_schema(sub) for sub in child]
        else:
            _semantic(child)
            if key == "type":
                types = child if isinstance(child, list) else [child]
                if (
                    not types
                    or any(
                        not isinstance(item, str) or item not in _TYPES
                        for item in types
                    )
                    or len(set(types)) != len(types)
                ):
                    raise ValueError("Invalid MCP type")
            elif key == "required":
                if (
                    not isinstance(child, list)
                    or any(not isinstance(item, str) for item in child)
                    or len(set(child)) != len(child)
                ):
                    raise ValueError("Invalid MCP required")
                properties = value.get("properties", {})
                if not isinstance(properties, dict) or not set(child) <= set(
                    properties
                ):
                    raise ValueError("Unknown MCP required property")
            elif key == "enum":
                if (
                    not isinstance(child, list)
                    or not child
                    or len({_encode(item) for item in child}) != len(child)
                ):
                    raise ValueError("Invalid MCP enum")
            elif key in _NUMERIC:
                if (
                    isinstance(child, bool)
                    or not isinstance(child, (int, float))
                    or (key == "multipleOf" and child <= 0)
                ):
                    raise ValueError("Invalid MCP numeric constraint")
            elif key in _COUNTS:
                if isinstance(child, bool) or not isinstance(child, int) or child < 0:
                    raise ValueError("Invalid MCP count constraint")
            elif key == "pattern":
                if not isinstance(child, str):
                    raise ValueError("Invalid MCP pattern")
                try:
                    re.compile(child)
                except re.error:
                    raise ValueError("Invalid MCP pattern") from None
            elif key == "uniqueItems" and not isinstance(child, bool):
                raise ValueError("Invalid MCP uniqueItems")
            result[key] = child
    return result


def sanitize_definition(
    raw: Mapping[str, Any], max_bytes: int
) -> tuple[MCPValidatedDefinition, Literal["unchanged", "sanitized"]]:
    """Validate complete bounded JSON, redact annotations, preserve safe semantics."""
    if len(_encode(raw).encode("utf-8")) > max_bytes:
        raise ValueError("MCP definition exceeds byte limit")
    _bounded_tree(raw)
    name = raw.get("name")
    description = raw.get("description", "")
    parameters = raw.get("inputSchema")
    if (
        not isinstance(name, str)
        or not name
        or len(name) > 256
        or not isinstance(description, str)
    ):
        raise ValueError("Invalid MCP definition")
    _semantic_text(name)
    if not isinstance(parameters, dict) or parameters.get("type") != "object":
        raise ValueError("MCP root schema must be object")
    # Scan even ignored peer extension/category fields: no partial-scan claim.
    for key, child in raw.items():
        _semantic_text(key)
        if key not in {"description", "inputSchema"}:
            _semantic(child)
    clean_description = _annotation(description)
    clean_parameters = _schema(parameters)
    changed = clean_description != description or clean_parameters != parameters
    return MCPValidatedDefinition(
        clean_description, _encode(clean_parameters)
    ), "sanitized" if changed else "unchanged"


def _selected(name: str, config: MCPToolProviderConfig) -> bool:
    selected = (
        (
            config.mode == "all"
            and (not config.include_categories or "mcp" in config.include_categories)
        )
        or "mcp" in config.include_categories
        or name in config.include_tools
    )
    return (
        selected
        and "mcp" not in config.exclude_categories
        and name not in config.exclude_tools
    )


def prepare_registration(
    config: MCPToolProviderConfig,
    entries: Iterable[MCPDiscoveryEntry],
    clients: Mapping[str, MCPClient],
    native_names: Iterable[str],
) -> MCPRegistrationPlan:
    """Pure admission/preflight: no mutations, no repeat tools/list or backfill."""
    limits = config.config.limits
    prefix = config.config.tool_name_prefix
    native = set(native_names)
    contenders: list[tuple[str, str, dict[str, Any]]] = []
    decisions: list[MCPRegistrationDecision] = []
    seen: dict[str, MCPCollisionSource] = {}
    for entry in entries:
        try:
            if (
                len(entry.untrusted_definition_json.encode("utf-8"))
                > limits.max_schema_bytes_per_tool
            ):
                raise ValueError("Oversized MCP handoff")
            raw: Any = json.loads(entry.untrusted_definition_json)
            if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
                raise ValueError("Invalid MCP handoff")
            name = normalize_mcp_tool_name(
                entry.server_id, raw["name"], tool_name_prefix=prefix
            )
        except (ValueError, TypeError, UnicodeError, RecursionError):
            decisions.append(
                MCPRegistrationDecision(
                    None, entry.server_id, "rejected", "invalid_schema"
                )
            )
            continue
        if name in seen or name in native:
            source = _mcp_collision_source(entry.server_id, raw["name"])
            first = seen[name] if name in seen else MCPCollisionSource("native")
            decisions.append(
                MCPRegistrationDecision(
                    name, entry.server_id, "rejected", "name_collision",
                    MCPNameCollision(name, first, source),
                )
            )
            raise MCPRegistrationError("name_collision", decisions) from None
        seen[name] = _mcp_collision_source(entry.server_id, raw["name"])
        contenders.append((entry.server_id, name, raw))

    wrappers: list[MCPToolWrapper] = []
    metadata: list[MCPToolMetadata] = []
    counts: dict[str, int] = {}
    cost = 0
    server_configs = {server.name: server for server in config.config.servers}
    for server_id, name, raw in contenders:
        try:
            definition, state = sanitize_definition(
                raw, limits.max_schema_bytes_per_tool
            )
        except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
            decisions.append(
                MCPRegistrationDecision(name, server_id, "rejected", "invalid_schema")
            )
            continue
        if not _selected(name, config):
            decisions.append(
                MCPRegistrationDecision(name, server_id, "filtered", "filter_excluded")
            )
            continue
        client = clients.get(server_id)
        server = server_configs.get(server_id)
        if client is None or server is None:
            decisions.append(
                MCPRegistrationDecision(
                    name, server_id, "unavailable", "connection_failed"
                )
            )
            continue
        if (
            len(wrappers) >= limits.max_total_tools
            or counts.get(server_id, 0) >= limits.max_tools_per_server
        ):
            decisions.append(
                MCPRegistrationDecision(name, server_id, "capped", "tool_limit")
            )
            continue
        item = MCPToolMetadata(
            canonical_name=name,
            server_name=server_id,
            original_name=raw["name"],
            tool_name_prefix=prefix,
            transport="stdio",
            trust_level=server.trust_level,
            discovery_state="discovered",
            schema_sanitization_state=state,
            filter_state="included",
        )
        wrapper = MCPToolWrapper.from_validated(client, item, definition)
        size = exported_definition_size(wrapper)
        if (
            size > limits.max_schema_bytes_per_tool
            or cost + size > limits.max_schema_tokens
        ):
            decisions.append(
                MCPRegistrationDecision(name, server_id, "capped", "schema_limit")
            )
            continue
        item = item.model_copy(
            update={"schema_byte_size": size, "schema_token_estimate": size}
        )
        wrappers.append(wrapper)
        metadata.append(item)
        counts[server_id] = counts.get(server_id, 0) + 1
        cost += size
        decisions.append(MCPRegistrationDecision(name, server_id, "selected"))
    missing = sorted(
        set(config.include_tools) - {item.canonical_name for item in metadata}
    )
    if missing:
        decisions.extend(
            MCPRegistrationDecision(name, None, "unknown", "missing_include")
            for name in missing
        )
        raise MCPRegistrationError("missing_include", decisions) from None
    return MCPRegistrationPlan(tuple(wrappers), tuple(metadata), tuple(decisions))
