"""Explicit endpoint policy enforced at httpcore's public connect boundary."""

from __future__ import annotations

import asyncio
import ipaddress
import socket
import ssl
from collections.abc import Callable, Iterable
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

import httpcore

from friday_mcp.client.protocol import ProtocolFailure

type SocketOption = (
    tuple[int, int, int]
    | tuple[int, int, bytes | bytearray]
    | tuple[int, int, None, int]
)


@dataclass(frozen=True)
class HTTPEndpointPolicy:
    """Exact-address/port opt-ins belong to one explicitly configured peer."""

    allowed_addresses: tuple[str, ...] = ()
    allowed_ports: tuple[int, ...] = (443,)
    allow_fixture_http: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.allowed_addresses, tuple)
            or len(self.allowed_addresses) > 16
            or not isinstance(self.allowed_ports, tuple)
            or not 0 < len(self.allowed_ports) <= 16
            or type(self.allow_fixture_http) is not bool
        ):
            raise ValueError("Invalid MCP HTTP policy")
        try:
            for address in self.allowed_addresses:
                if (
                    not isinstance(address, str)
                    or str(ipaddress.ip_address(address)) != address
                ):
                    raise ValueError
        except ValueError:
            raise ValueError("Invalid MCP HTTP policy") from None
        if any(
            type(port) is not int or not 0 < port < 65536 for port in self.allowed_ports
        ):
            raise ValueError("Invalid MCP HTTP policy")

    def permits(self, address: str) -> bool:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False
        # Reject mapped IPv6 addresses rather than relying on changing class rules.
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            return False
        return str(ip) in self.allowed_addresses or (
            ip.is_global
            and not ip.is_multicast
            and not ip.is_reserved
            and not ip.is_unspecified
            and not ip.is_loopback
            and not ip.is_link_local
        )


@dataclass(frozen=True)
class HTTPEndpoint:
    url: str = field(repr=False)
    host: str = field(repr=False)
    port: int
    scheme: str
    policy: HTTPEndpointPolicy

    @classmethod
    def parse(cls, url: str, policy: HTTPEndpointPolicy) -> HTTPEndpoint:
        if (
            not isinstance(url, str)
            or not 0 < len(url) <= 4096
            or any(not 0x21 <= ord(c) <= 0x7E for c in url)
            or any(c in url for c in ("?", "#", "\\"))
            or not isinstance(policy, HTTPEndpointPolicy)
        ):
            raise ValueError("Invalid MCP HTTP endpoint")
        try:
            parsed = urlsplit(url)
            host = parsed.hostname
            port = (
                parsed.port
                if parsed.port is not None
                else (443 if parsed.scheme == "https" else 80)
            )
            if not host or parsed.username is not None or parsed.password is not None:
                raise ValueError
            if (
                parsed.scheme not in ("https", "http")
                or port not in policy.allowed_ports
            ):
                raise ValueError
            # DNS names are ASCII/punycode, with no escaped host or IPv6 zone IDs.
            if "%" in host or any(
                c not in "abcdefghijklmnopqrstuvwxyz0123456789.-:" for c in host
            ):
                raise ValueError
            try:
                literal = str(ipaddress.ip_address(host))
            except ValueError:
                literal = None
            if literal is not None and not policy.permits(literal):
                raise ValueError
            if parsed.scheme == "http" and (
                not policy.allow_fixture_http
                or host != "127.0.0.1"
                or "127.0.0.1" not in policy.allowed_addresses
            ):
                raise ValueError
            authority = f"[{host}]" if ":" in host else host
            if parsed.port is not None:
                authority += f":{port}"
            normalized = urlunsplit(
                (parsed.scheme, authority, parsed.path or "/", "", "")
            )
        except ValueError:
            raise ValueError("Invalid MCP HTTP endpoint") from None
        return cls(normalized, host, port, parsed.scheme, policy)


class HTTPResolver(Protocol):
    async def resolve(self, host: str, port: int) -> tuple[str, ...]: ...


class SystemHTTPResolver:
    async def resolve(self, host: str, port: int) -> tuple[str, ...]:
        try:
            return (str(ipaddress.ip_address(host)),)
        except ValueError:
            pass
        answers = await asyncio.get_running_loop().getaddrinfo(
            host, port, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        if not 0 < len(answers) <= 16:
            raise ProtocolFailure("limit_exceeded")
        return tuple(dict.fromkeys(str(answer[4][0]) for answer in answers))


class AsyncioHTTPStream(httpcore.AsyncNetworkStream):
    """Owned socket adapter; TLS retains httpcore's original hostname."""

    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self.reader = reader
        self.writer = writer

    async def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        try:
            async with asyncio.timeout(timeout):
                return await self.reader.read(max_bytes)
        except TimeoutError:
            raise TimeoutError("MCP HTTP timeout") from None
        except Exception:
            raise ProtocolFailure() from None

    async def write(self, buffer: bytes, timeout: float | None = None) -> None:
        try:
            async with asyncio.timeout(timeout):
                self.writer.write(buffer)
                await self.writer.drain()
        except TimeoutError:
            raise TimeoutError("MCP HTTP timeout") from None
        except Exception:
            raise ProtocolFailure() from None

    async def aclose(self) -> None:
        try:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except (ssl.SSLError, ConnectionError):
                # Failed TLS can leave an exceptional close waiter. Explicit
                # abort closes the owned socket, rather than retrying that waiter.
                self.writer.transport.abort()
                await asyncio.sleep(0)
        except Exception:
            raise ProtocolFailure() from None

    async def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore.AsyncNetworkStream:
        try:
            await self.writer.start_tls(
                ssl_context,
                server_hostname=server_hostname,
                ssl_handshake_timeout=timeout,
            )
        except Exception:
            raise ProtocolFailure() from None
        return self

    def get_extra_info(self, info: str) -> object:
        # Public httpcore selector boundary; arbitrary attributes are not exposed.
        if info == "is_readable":
            return self.reader.at_eof()
        if info in ("ssl_object", "socket", "peername", "sockname"):
            return self.writer.get_extra_info(info)
        return None


class AsyncioHTTPBackend(httpcore.AsyncNetworkBackend):
    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[SocketOption] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        # Connect only to a numeric address, without resolving the hostname again.
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            raise ProtocolFailure() from None
        if local_address is not None or socket_options:
            raise ProtocolFailure()
        async with asyncio.timeout(timeout):
            reader, writer = await asyncio.open_connection(
                str(address),
                port,
                family=socket.AF_INET if address.version == 4 else socket.AF_INET6,
            )
        return AsyncioHTTPStream(reader, writer)


class BoundedHTTPStream(httpcore.AsyncNetworkStream):
    """Bound wire/header bytes before httpcore/h11 decodes response headers."""

    def __init__(
        self,
        stream: httpcore.AsyncNetworkStream,
        header_bytes: int,
        wire_bytes: int,
    ) -> None:
        self.stream = stream
        self.header_bytes = header_bytes
        self.wire_limit = wire_bytes
        self.received = 0
        self.headers_received = 0
        self.head = bytearray()
        self.reading_headers = True
        self.sent_header = bytearray()
        self.sent_headers_done = False
        self.closed = False
        self.owner = ""
        self.on_issue: Callable[[], None] | None = None
        self.issued = False
        self.body_sent = 0
        self.body_expected = 0

    async def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        data = await self.stream.read(
            min(max_bytes, 16384, self.wire_limit - self.received + 1), timeout
        )
        self.received += len(data)
        if self.received > self.wire_limit:
            raise ProtocolFailure("limit_exceeded")
        if self.reading_headers:
            # Retain only the bounded header, including repeated informational heads.
            for byte in data:
                self.headers_received += 1
                if self.headers_received > self.header_bytes:
                    raise ProtocolFailure("limit_exceeded")
                self.head.append(byte)
                if self.head.endswith(b"\r\n\r\n"):
                    line = bytes(self.head).split(b"\r\n", 1)[0].split(b" ")
                    informational = len(line) >= 2 and line[1].startswith(b"1")
                    self.head.clear()
                    if not informational:
                        self.reading_headers = False
                        break
        return data

    async def write(self, buffer: bytes, timeout: float | None = None) -> None:
        body_bytes = len(buffer) if self.sent_headers_done else 0
        if not self.sent_headers_done:
            for offset, byte in enumerate(buffer):
                self.sent_header.append(byte)
                if len(self.sent_header) > self.header_bytes:
                    raise ProtocolFailure("limit_exceeded")
                if self.sent_header.endswith(b"\r\n\r\n"):
                    fields = bytes(self.sent_header).split(b"\r\n")[1:]
                    for line in fields:
                        if line.lower().startswith(b"content-length:"):
                            self.body_expected = int(line.split(b":", 1)[1].strip())
                    self.sent_headers_done = True
                    self.sent_header.clear()
                    body_bytes = len(buffer) - offset - 1
                    break
        await self.stream.write(buffer, timeout)
        self.body_sent += body_bytes
        if (
            self.sent_headers_done
            and self.body_sent >= self.body_expected
            and not self.issued
        ):
            self.issued = True
            if self.on_issue is not None:
                self.on_issue()

    async def aclose(self) -> None:
        try:
            await self.stream.aclose()
        except Exception:
            raise ProtocolFailure() from None
        self.closed = True

    async def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore.AsyncNetworkStream:
        try:
            self.stream = await self.stream.start_tls(
                ssl_context, server_hostname, timeout
            )
        except Exception:
            raise ProtocolFailure() from None
        return self

    def get_extra_info(self, info: str) -> object:
        return self.stream.get_extra_info(info)


class PolicyHTTPBackend(httpcore.AsyncNetworkBackend):
    """Borrowed resolver/connector, owned returned streams; every connect is checked."""

    def __init__(
        self,
        endpoint: HTTPEndpoint,
        header_bytes: int,
        wire_bytes: int,
        resolver: HTTPResolver | None = None,
        connector: httpcore.AsyncNetworkBackend | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.header_bytes = header_bytes
        self.wire_bytes = wire_bytes
        self.resolver = resolver or SystemHTTPResolver()
        self.connector = connector or AsyncioHTTPBackend()
        self.streams: set[BoundedHTTPStream] = set()
        self.owner: ContextVar[str] = ContextVar("mcp_http_owner", default="")
        self.issued: set[str] = set()

    async def aclose(self) -> None:
        for stream in tuple(self.streams):
            if not stream.closed:
                await stream.aclose()
            self.streams.discard(stream)

    async def close_owner(self, owner: str) -> None:
        for stream in tuple(self.streams):
            if stream.owner == owner:
                if not stream.closed:
                    await stream.aclose()
                self.streams.discard(stream)

    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[SocketOption] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        if (
            host != self.endpoint.host
            or port != self.endpoint.port
            or local_address is not None
        ):
            raise ProtocolFailure()
        async with asyncio.timeout(timeout):
            answers = await self.resolver.resolve(host, port)
            if not isinstance(answers, tuple) or not 0 < len(answers) <= 16:
                raise ProtocolFailure()
            if any(
                not isinstance(a, str) or not self.endpoint.policy.permits(a)
                for a in answers
            ):
                raise ProtocolFailure()
            address = str(ipaddress.ip_address(answers[0]))
            stream = await self.connector.connect_tcp(
                address, port, timeout, None, socket_options
            )
            bounded = BoundedHTTPStream(stream, self.header_bytes, self.wire_bytes)
            bounded.owner = self.owner.get()
            bounded.on_issue = lambda: self.issued.add(bounded.owner)
            self.streams = {s for s in self.streams if not s.closed}
            self.streams.add(bounded)
            return bounded
