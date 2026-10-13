"""Explicit server exposure policy and dated HTTP metadata validation."""

from __future__ import annotations

import base64
import binascii
import hmac
import ipaddress
import math
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from friday_mcp.client.protocol import JSONValue
from friday_mcp.server.protocol import (
    RegisteredTool,
    ServerLimits,
    ServerRequest,
    ServerWireError,
)

_TOKEN = re.compile(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")
_AUTHORITY = re.compile(
    r"(?:[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?|\[[0-9a-f:]+\])(?::[0-9]{1,5})?\Z"
)


class HTTPAccessError(ValueError):
    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__("MCP HTTP access rejected")


def _authority(value: str) -> bool:
    if (
        not value
        or len(value) > 256
        or _AUTHORITY.fullmatch(value) is None
        or ".." in value
    ):
        return False
    try:
        parsed = urlsplit("https://" + value)
        return parsed.hostname is not None and (
            parsed.port is None or 0 < parsed.port <= 65535
        )
    except ValueError:
        return False


def _origin(value: str) -> bool:
    if not value or any(not 0x21 <= ord(c) <= 0x7E for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme in ("http", "https")
            and _authority(parsed.netloc)
            and not (
                parsed.path
                or parsed.query
                or parsed.fragment
                or parsed.username
                or parsed.password
            )
        )
    except ValueError:
        return False


@dataclass(frozen=True)
class HTTPServerPolicy:
    """Administrative access, not delegated OAuth. No credential discovery."""

    path: str = "/mcp"
    bind_host: str = "127.0.0.1"
    port: int = 8000
    allowed_hosts: tuple[str, ...] = ()
    allowed_origins: tuple[str, ...] = ()
    bearer_token: str | None = field(default=None, repr=False, compare=False)
    require_tls: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.path, str)
            or not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+", self.path)
            or len(self.path) > 256
        ):
            raise ValueError("Invalid MCP HTTP policy")
        if (
            type(self.port) is not int
            or not 0 < self.port <= 65535
            or type(self.require_tls) is not bool
        ):
            raise ValueError("Invalid MCP HTTP policy")
        if not isinstance(self.bind_host, str):
            raise ValueError("Invalid MCP HTTP policy")
        try:
            address = ipaddress.ip_address(self.bind_host)
        except ValueError:
            raise ValueError("Invalid MCP HTTP policy") from None
        if (
            not isinstance(self.allowed_hosts, tuple)
            or not isinstance(self.allowed_origins, tuple)
            or any(
                not isinstance(h, str) or not _authority(h) for h in self.allowed_hosts
            )
            or any(
                not isinstance(o, str) or not _origin(o) for o in self.allowed_origins
            )
        ):
            raise ValueError("Invalid MCP HTTP policy")
        if self.bearer_token is not None and (
            not isinstance(self.bearer_token, str)
            or not self.bearer_token
            or len(self.bearer_token) > 4096
            or any(not 0x21 <= ord(c) <= 0x7E for c in self.bearer_token)
        ):
            raise ValueError("Invalid MCP HTTP policy")
        if not address.is_loopback and (
            not self.allowed_hosts
            or not self.allowed_origins
            or self.bearer_token is None
            or not self.require_tls
        ):
            raise ValueError("Nonlocal MCP requires explicit TLS and access policy")

    def validate(
        self,
        pairs: list[tuple[bytes, bytes]],
        *,
        scheme: str,
        query: bytes,
        limits: ServerLimits,
    ) -> dict[bytes, bytes]:
        headers: dict[bytes, bytes] = {}
        size = 0
        for name, value in pairs:
            size += len(name) + len(value) + 4
            lower = name.lower()
            if size > limits.header_bytes:
                raise HTTPAccessError(400)
            mirrored = lower in (
                b"mcp-protocol-version",
                b"mcp-method",
                b"mcp-name",
            ) or lower.startswith(b"mcp-param-")
            if mirrored and (
                lower in headers or any(c in value for c in (b"\r", b"\n", b"\0"))
            ):
                raise ServerWireError(-32020)
            if (
                size > limits.header_bytes
                or _TOKEN.fullmatch(name) is None
                or lower in headers
                or any(c in value for c in (b"\r", b"\n", b"\0"))
            ):
                raise HTTPAccessError(400)
            headers[lower] = value
        if b"origin" in headers:
            try:
                origin = headers[b"origin"].decode("ascii")
            except UnicodeError:
                raise HTTPAccessError(403) from None
            if not _origin(origin) or origin not in self.allowed_origins:
                raise HTTPAccessError(403)
        try:
            host = headers.get(b"host", b"").decode("ascii").lower()
            expected = self.allowed_hosts or (
                (
                    f"[{self.bind_host}]:{self.port}"
                    if ":" in self.bind_host
                    else f"{self.bind_host}:{self.port}"
                ),
            )
            if not _authority(host) or host not in expected:
                raise HTTPAccessError(400)
            if self.require_tls and scheme != "https":
                raise HTTPAccessError(400)
        except UnicodeError:
            raise HTTPAccessError(400) from None
        if query:
            raise HTTPAccessError(400)
        if self.bearer_token is not None:
            auth_scheme, separator, credential = headers.get(
                b"authorization", b""
            ).partition(b" ")
            if (
                auth_scheme.lower() != b"bearer"
                or not separator
                or not hmac.compare_digest(
                    credential, self.bearer_token.encode("ascii")
                )
            ):
                raise HTTPAccessError(401)
        elif b"authorization" in headers:
            raise HTTPAccessError(401)
        return headers


def decode_header(raw: bytes) -> str:
    try:
        if raw.startswith(b"=?base64?") and raw.endswith(b"?="):
            payload = raw[9:-2]
            value = base64.b64decode(payload, validate=True)
            if base64.b64encode(value) != payload:
                raise ServerWireError(-32020)
            return value.decode("utf-8")
        text = raw.decode("ascii")
        if text != text.strip() or any(
            not (0x20 <= ord(c) <= 0x7E or c == "\t") for c in text
        ):
            raise ServerWireError(-32020)
        return text
    except (UnicodeError, binascii.Error, ValueError):
        raise ServerWireError(-32020) from None


def validate_rpc_headers(
    headers: dict[bytes, bytes], request: ServerRequest, tool: RegisteredTool | None
) -> None:
    if request.request_id is None:
        # No core HTTP client notifications exist in this revision.
        raise ServerWireError(-32601)
    if headers.get(b"mcp-protocol-version") != (request.version or "").encode(
        "utf-8"
    ) or headers.get(b"mcp-method") != request.method.encode("utf-8"):
        raise ServerWireError(-32020)
    if request.method in ("tools/call", "prompts/get", "resources/read"):
        name = request.params.get(
            "uri" if request.method == "resources/read" else "name"
        )
        if not isinstance(name, str):
            raise ServerWireError(-32602)
        if b"mcp-name" not in headers or decode_header(headers[b"mcp-name"]) != name:
            raise ServerWireError(-32020)
    if tool is None:
        return
    args = request.params.get("arguments", {})
    if not isinstance(args, dict):
        raise ServerWireError(-32602)
    for binding in tool.bindings:
        value: JSONValue = args
        for key in binding.path:
            if value is None:
                break
            if not isinstance(value, dict):
                raise ServerWireError(-32020)
            value = value.get(key)
        header = headers.get(b"mcp-param-" + binding.name.lower().encode("ascii"))
        if value is None:
            if header is not None:
                raise ServerWireError(-32020)
            continue
        if header is None:
            raise ServerWireError(-32020)
        text = decode_header(header)
        if binding.kind == "string":
            if not isinstance(value, str) or text != value:
                raise ServerWireError(-32020)
        elif binding.kind == "boolean":
            if type(value) is not bool or text != ("true" if value else "false"):
                raise ServerWireError(-32020)
        else:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or abs(value) > 2**53 - 1
                or int(value) != value
            ):
                raise ServerWireError(-32020)
            if (
                re.fullmatch(
                    r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", text
                )
                is None
            ):
                raise ServerWireError(-32020)
            try:
                number = Decimal(text)
            except InvalidOperation:
                raise ServerWireError(-32020) from None
            if not number.is_finite() or number != int(value):
                raise ServerWireError(-32020)


def validate_media_headers(headers: dict[bytes, bytes]) -> None:
    content = headers.get(b"content-type", b"").split(b";")
    if content[0].strip().lower() != b"application/json":
        raise ServerWireError(-32600)
    seen: set[bytes] = set()
    for parameter in content[1:]:
        key, separator, value = parameter.strip().partition(b"=")
        key = key.lower()
        if (
            not separator
            or key != b"charset"
            or key in seen
            or value.strip().lower() not in (b"utf-8", b'"utf-8"')
        ):
            raise ServerWireError(-32600)
        seen.add(key)
    accepted: set[bytes] = set()
    for part in headers.get(b"accept", b"").split(b","):
        fields = part.split(b";")
        media = fields[0].strip().lower()
        if (
            re.fullmatch(
                rb"(?:[!#$%&'*+.^_`|~0-9A-Za-z-]+|\*)/(?:[!#$%&'*+.^_`|~0-9A-Za-z-]+|\*)",
                media,
            )
            is None
        ):
            raise ServerWireError(-32600)
        quality = 1.0
        quality_seen = False
        for field_value in fields[1:]:
            key, separator, value = field_value.strip().partition(b"=")
            if (
                not separator
                or key.lower() != b"q"
                or quality_seen
                or re.fullmatch(
                    rb"(?:0(?:\.[0-9]{0,3})?|1(?:\.0{0,3})?)", value.strip()
                )
                is None
            ):
                raise ServerWireError(-32600)
            quality = float(value.strip())
            quality_seen = True
        if quality > 0:
            accepted.add(media)
    if not {b"application/json", b"text/event-stream"}.issubset(accepted):
        raise ServerWireError(-32600)
